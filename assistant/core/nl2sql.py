# assistant/core/nl2sql.py
# ================================================================
# Version 2.0 — Intégré avec sql_validator v2.0 (auto-correction)
# ================================================================

import json
import re
from typing import Any, Dict

from assistant.prompts.system_prompt import get_system_prompt
from assistant.core.config import ALLOWED_INTENTS, BQ_PROJECT, BQ_DATASET
from assistant.core.sql_validator import (
    validate_sql,
    auto_correct_sql,               # ← NOUVEAU v2
    SQLValidationException,
)
from assistant.core.response_builder import (
    build_sql_error_response,
    build_empty_result_response,
    build_result_too_large_response,
    build_success_response,
)
from assistant.core.bigquery_runner import BigQueryRunner
from assistant.core.logger import log_interaction
from assistant.core.llm_client import llm_chat


class NL2SQLException(Exception):
    pass


MAX_DISPLAY_ROWS = 500
MAX_RETRIES = 1                    # ← NOUVEAU v2 : 1 retry après auto-correction
_bq_runner = None  # Variable globale, non initialisée

def get_bq_runner() -> BigQueryRunner:
    global _bq_runner
    if _bq_runner is None:
        _bq_runner = BigQueryRunner()  # Créé au PREMIER APPEL, pas à l'import
    return _bq_runner
_AUTHORIZED_JOIN_KEY = "GLOBALEVENTID"

_HALLUCINATED_COLUMNS = [
    r"\bactor_id\b",
    r"\bevent_id\b",
    r"\barticle_id\b",
    r"\bsource_id\b",
    r"\bgkg_id\b",
]


# ─────────────────────────────────────────────────────────────
# Utilitaires JSON
# ─────────────────────────────────────────────────────────────

def _strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    for prefix in ("```json", "```"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned


def _extract_json(text: str) -> str:
    """Extrait le premier objet JSON { ... } de la réponse brute."""
    cleaned = _strip_json_fence(text)
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise NL2SQLException(
            f"Aucun JSON détecté dans la réponse LLM : {cleaned[:200]}"
        )
    return cleaned[start : end + 1]


def _empty_plan() -> Dict[str, Any]:
    """
    Plan vide retourné quand le parsing échoue — évite un 2e appel LLM.
    """
    return {
        "intent": "unknown",
        "tables": [],
        "sql": "",
        "chart_recommendation": "table",
        "explanation_hint": (
            "Le modèle n'a pas pu générer de requête valide. "
            "Reformulez ou simplifiez votre question."
        ),
        "reasoning_steps": [],
    }


# ─────────────────────────────────────────────────────────────
# Validation SQL post-parse (rapide, locale)
# ─────────────────────────────────────────────────────────────

def _extract_alias_table_map(sql: str) -> Dict[str, str]:
    """
    Extrait les alias déclarés dans FROM/JOIN.
    """
    alias_map: Dict[str, str] = {}
    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+`[^`]+\."
        r"(events_clean|mentions_clean|gkg_clean)`"
        r"(?:\s+AS)?\s+(\w+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(sql):
        table_name = match.group(1)
        alias = match.group(2)
        alias_map[alias] = table_name
    return alias_map


def _validate_join_keys(sql: str) -> None:
    """
    Vérifie que les jointures utilisent uniquement GLOBALEVENTID
    entre events_clean et mentions_clean.
    """
    alias_map = _extract_alias_table_map(sql)
    pattern = re.compile(
        r"\bON\b\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(sql):
        left_alias, left_col, right_alias, right_col = match.groups()

        if (left_col.upper() != _AUTHORIZED_JOIN_KEY
                or right_col.upper() != _AUTHORIZED_JOIN_KEY):
            raise NL2SQLException(
                f"Jointure interdite : ON {left_alias}.{left_col} = "
                f"{right_alias}.{right_col}. "
                f"Seule la clé '{_AUTHORIZED_JOIN_KEY}' est autorisée."
            )

        if left_alias == right_alias:
            raise NL2SQLException(
                f"Jointure invalide : les alias doivent être différents "
                f"({left_alias}.{left_col} = {right_alias}.{right_col})."
            )

        left_table = alias_map.get(left_alias)
        right_table = alias_map.get(right_alias)

        if left_table and right_table:
            allowed_pair = {"events_clean", "mentions_clean"}
            actual_pair = {left_table, right_table}
            if actual_pair != allowed_pair:
                raise NL2SQLException(
                    f"Jointure interdite entre {left_table} et {right_table}. "
                    "Seule events_clean ↔ mentions_clean est autorisée."
                )


def _validate_no_hallucinated_columns(sql: str) -> None:
    """Détection rapide de colonnes fréquemment inventées."""
    sql_lower = sql.lower()
    for pattern in _HALLUCINATED_COLUMNS:
        if re.search(pattern, sql_lower):
            raise NL2SQLException(
                f"Colonne inventée détectée (pattern : {pattern})."
            )


def _post_validate_sql(sql: str) -> None:
    """Validations légères locales avant la validation structurelle."""
    if not sql:
        return
    _validate_join_keys(sql)
    _validate_no_hallucinated_columns(sql)


# ─────────────────────────────────────────────────────────────
# Appel LLM principal
# ─────────────────────────────────────────────────────────────

def call_llm_for_nl2sql(user_question: str) -> Dict[str, Any]:
    """
    Envoie la question au LLM et parse le JSON retourné.
    En cas d'échec de parsing → retourne un plan vide.
    """
    system_prompt = get_system_prompt(user_question=user_question)

    try:
        response_text = llm_chat(system=system_prompt, user=user_question)
    except Exception as e:
        raise NL2SQLException(f"Erreur appel LLM : {e}") from e

    try:
        json_str = _extract_json(response_text)
        parsed = json.loads(json_str)
    except (NL2SQLException, json.JSONDecodeError):
        return _empty_plan()

    # Champs critiques + défauts
    parsed.setdefault("intent", "unknown")
    parsed.setdefault("tables", [])
    parsed.setdefault("sql", "")
    parsed.setdefault("chart_recommendation", "table")
    parsed.setdefault("explanation_hint", "")
    parsed.setdefault("reasoning_steps", [])

    # Intent autorisé seulement
    if parsed["intent"] not in ALLOWED_INTENTS:
        parsed["intent"] = "unknown"

    if not parsed.get("sql"):
        if not parsed.get("explanation_hint"):
            parsed["explanation_hint"] = (
                "Le modèle n'a pas généré de SQL. "
                "Reformulez ou simplifiez votre question."
            )

    # Validation rapide locale (jointures, colonnes hallucinées)
    # ← CHANGÉ v2 : on applique d'abord l'auto-correction avant la validation locale
    raw_sql = parsed.get("sql", "")
    if raw_sql:
        corrected_sql, corrections = auto_correct_sql(raw_sql)
        parsed["sql"] = corrected_sql
        if corrections:
            parsed.setdefault("auto_corrections", corrections)

    _post_validate_sql(parsed.get("sql", ""))

    return parsed


# ─────────────────────────────────────────────────────────────
# Pipeline NL2SQL
# ─────────────────────────────────────────────────────────────

def generate_sql_plan(user_question: str) -> Dict[str, Any]:
    """
    Question → JSON plan validé, prêt à exécution.
    """
    nl2sql_result = call_llm_for_nl2sql(user_question)

    sql = nl2sql_result.get("sql", "")
    if not sql:
        raise NL2SQLException(
            nl2sql_result.get(
                "explanation_hint",
                "Le modèle n'a pas généré de SQL.",
            )
        )

    # ← CHANGÉ v2 : validate_sql() retourne le SQL corrigé (str)
    validated_sql = validate_sql(
        sql,
        expected_tables=nl2sql_result["tables"],
        project=BQ_PROJECT,
        dataset=BQ_DATASET,
        validate_columns=True,
        auto_correct=True,           # ← NOUVEAU v2 : double auto-correction
    )

    # ← CHANGÉ v2 : on utilise le SQL corrigé par le validateur
    nl2sql_result["sql"] = validated_sql

    return nl2sql_result


def process_user_question(user_question: str) -> Dict[str, Any]:
    """
    Orchestrateur complet :
    question → plan NL2SQL → validation → exécution BigQuery → résultat
    """
    try:
        plan = generate_sql_plan(user_question)
    except (NL2SQLException, SQLValidationException) as e:
        log_interaction(
            user_question=user_question,
            sql=None,
            status="sql_error",
            error=str(e),
        )
        return build_sql_error_response(
            message="La requête n'a pas passé les règles de sécurité "
                    "ou de structure.",
            details=str(e),
        )
    except Exception as e:
        log_interaction(
            user_question=user_question,
            sql=None,
            status="sql_error",
            error=str(e),
        )
        return build_sql_error_response(
            message="Erreur inattendue lors de la génération de la requête.",
            details=str(e),
        )

    # ← CHANGÉ v2 : sql est déjà corrigé par validate_sql()
    sql = plan["sql"]

    # ← NOUVEAU v2 : log des auto-corrections si présentes
    auto_corrections = plan.get("auto_corrections", [])
    if auto_corrections:
        log_interaction(
            user_question=user_question,
            sql=sql,
            status="auto_corrected",
            error=f"Corrections appliquées : {', '.join(auto_corrections)}",
        )

    try:
        df, meta = get_bq_runner().run_query(sql)
    except Exception as e:
        log_interaction(
            user_question=user_question,
            sql=sql,
            status="sql_error",
            error=str(e),
        )
        return build_sql_error_response(
            message="Erreur lors de l'exécution sur BigQuery.",
            details=str(e),
        )

    if df.empty:
        log_interaction(
            user_question=user_question,
            sql=sql,
            status="empty_result",
            row_count=0,
            time_seconds=meta.get("time_seconds"),
        )
        return build_empty_result_response()

    if meta["row_count"] > MAX_DISPLAY_ROWS:
        log_interaction(
            user_question=user_question,
            sql=sql,
            status="result_too_large",
            row_count=meta["row_count"],
            time_seconds=meta.get("time_seconds"),
        )
        return build_result_too_large_response(
            row_count=meta["row_count"],
            max_display_rows=MAX_DISPLAY_ROWS,
        )

    log_interaction(
        user_question=user_question,
        sql=sql,
        status="success",
        row_count=meta["row_count"],
        time_seconds=meta.get("time_seconds"),
    )

    return build_success_response(
        sql=sql,
        rows=df.to_dict(orient="records"),
        chart_type=plan.get("chart_recommendation"),
        title=plan.get("explanation_hint"),
    )