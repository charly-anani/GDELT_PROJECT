# assistant/core/sql_validator.py
# ================================================================
# GDELT BÉNIN 2025 — SQL Validator v2.0
# ================================================================
# Valide et auto-corrige les requêtes SQL générées par le LLM.
#
# Améliorations v2.0 :
#   - Auto-correction des erreurs fréquentes (ANTI_PATTERNS)
#   - Résolution d'alias + vérification colonne → table
#   - Gestion des alias UNNEST (theme, person, org, location)
#   - Suggestions de colonnes proches en cas d'erreur
#   - Retourne le SQL corrigé (au lieu de None)
# ================================================================

import re
from difflib import get_close_matches
from typing import Dict, List, Optional, Set, Tuple


# ════════════════════════════════════════════════════════════════
# IMPORTS DEPUIS column_dictionary (avec fallback inline)
# ════════════════════════════════════════════════════════════════

try:
    from assistant.metadata.column_dictionary import (
        VALID_COLUMNS,
        ANTI_PATTERNS,
        TABLE_RELATIONSHIPS,
    )
except ImportError:
    # Fallback : définition inline si l'import échoue
    VALID_COLUMNS = None
    ANTI_PATTERNS = None
    TABLE_RELATIONSHIPS = None


# ════════════════════════════════════════════════════════════════
# CONSTANTES DE SÉCURITÉ
# ════════════════════════════════════════════════════════════════

FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE",
    "MERGE", "REPLACE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
    "CALL", "CREATE",
]

TIME_FILTER_PATTERNS = [
    r"\bYear\s*=\s*2025\b",
    r"\byear_month_clean\b",
    r"\bdate_clean\b",
    r"\bmention_year_month\b",
    r"\bmention_date\b",
    r"\bmention_datetime\b",
    r"\bgkg_year_month\b",
    r"\bgkg_date\b",
    r"\bgkg_datetime\b",
    r"\bMonthYear\b",
    r"\bSQLDATE\b",
    r"\bDATEADDED\b",
    r"\bMentionTimeDate\b",
    r"\b2025\b",
]

DEFAULT_ALLOWED_TABLES: Set[str] = {
    "gdelt-494812.benin_2025.events_clean",
    "gdelt-494812.benin_2025.mentions_clean",
    "gdelt-494812.benin_2025.gkg_clean",
}

# Alias générés par UNNEST — ne pas valider comme alias.colonne
UNNEST_ALIASES = {
    "theme", "themes", "person", "persons", "org", "orgs",
    "organization", "organizations", "location", "locations",
}

# Fonctions SQL / mots réservés à ignorer dans la détection alias.colonne
SQL_FUNCTIONS_AND_KEYWORDS = {
    "COUNT", "SUM", "AVG", "MIN", "MAX", "ROUND", "COALESCE",
    "IFNULL", "NULLIF", "CAST", "EXTRACT", "FORMAT", "PARSE",
    "DATE", "TIMESTAMP", "STRING", "INT64", "FLOAT64", "BOOL",
    "CASE", "WHEN", "THEN", "ELSE", "END", "AND", "OR", "NOT",
    "IN", "IS", "NULL", "TRUE", "FALSE", "LIKE", "BETWEEN",
    "AS", "ON", "BY", "ASC", "DESC", "LIMIT", "OFFSET",
    "HAVING", "WHERE", "FROM", "JOIN", "LEFT", "RIGHT", "INNER",
    "OUTER", "FULL", "CROSS", "GROUP", "ORDER", "SELECT", "WITH",
    "DISTINCT", "ALL", "UNION", "INTERSECT", "EXCEPT", "EXISTS",
    "UNNEST", "SPLIT", "ARRAY", "STRUCT", "OVER", "PARTITION",
    "ROW_NUMBER", "RANK", "DENSE_RANK", "LAG", "LEAD",
    "FIRST_VALUE", "LAST_VALUE", "QUALIFY",
}


# ════════════════════════════════════════════════════════════════
# SCHÉMA DES COLONNES (fallback si VALID_COLUMNS non importé)
# ════════════════════════════════════════════════════════════════

SCHEMA_COLUMNS: Dict[str, Set[str]] = {
    "events_clean": {
        "GLOBALEVENTID", "DATEADDED", "SQLDATE", "MonthYear", "Year",
        "Actor1Name", "Actor1CountryCode", "Actor1Type1Code",
        "Actor2Name", "Actor2CountryCode", "Actor2Type1Code",
        "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
        "QuadClass", "GoldsteinScale", "NumMentions", "NumSources", "NumArticles",
        "AvgTone", "ActionGeo_FullName", "ActionGeo_CountryCode", "ActionGeo_ADM1Code",
        "ActionGeo_Lat", "ActionGeo_Long", "SOURCEURL",
        "date_clean", "year_month_clean",
        "QuadClass_Label", "interaction_type", "EventCategory",
        "Actor1Role", "Actor2Role", "goldstein_category", "tone_category",
        "has_international_actor", "event_scope", "is_significant",
    },
    "mentions_clean": {
        "GLOBALEVENTID", "MentionTimeDate", "MentionType", "MentionSourceName",
        "Confidence", "MentionDocTone", "MentionDocTranslationInfo",
        "mention_datetime", "mention_date", "mention_year_month",
        "MentionType_Label", "tone_category", "confidence_level",
        "source_language", "is_translated",
    },
    "gkg_clean": {
        "GKGRECORDID", "DATE", "SourceCommonName", "DocumentIdentifier",
        "V2Themes", "V2Locations", "V2Persons", "V2Organizations",
        "V2Tone", "TranslationInfo", "SharingImage",
        "gkg_datetime", "gkg_date", "gkg_year_month",
        "tone", "tone_positive", "tone_negative", "tone_polarity",
        "tone_activity", "word_count", "tone_category",
        "source_language", "is_translated",
        "nb_themes", "nb_persons", "nb_organizations", "nb_locations",
        "is_rich_article",
    },
}


def _get_schema() -> Dict[str, Set[str]]:
    """Retourne le schéma depuis column_dictionary si disponible, sinon fallback inline."""
    if VALID_COLUMNS:
        return {table: set(cols) for table, cols in VALID_COLUMNS.items()}
    return SCHEMA_COLUMNS


# ════════════════════════════════════════════════════════════════
# EXCEPTION
# ════════════════════════════════════════════════════════════════

class SQLValidationException(Exception):
    pass


# ════════════════════════════════════════════════════════════════
# NORMALISATION
# ════════════════════════════════════════════════════════════════

def _normalize_sql(sql: str) -> str:
    """Normalise les espaces, supprime les retours à la ligne multiples."""
    if not sql:
        return ""
    sql = sql.strip().rstrip(";").strip()
    sql = re.sub(r"\s+", " ", sql)
    return sql


# ════════════════════════════════════════════════════════════════
# AUTO-CORRECTION DES ERREURS LLM
# ════════════════════════════════════════════════════════════════

# Mapping statique des corrections fréquentes (nommage CamelCase → snake_case)
_COLUMN_NAME_CORRECTIONS = {
    # mentions_clean — nommage
    "MentionYearMonth":       "mention_year_month",
    "mentionyearmonth":       "mention_year_month",
    "MentionDate":            "mention_date",
    "mentiondate":            "mention_date",
    "MentionDateTime":        "mention_datetime",
    "mentiondatetime":        "mention_datetime",
    # events_clean — nommage
    "YearMonthClean":         "year_month_clean",
    "yearmonthclean":         "year_month_clean",
    "DateClean":              "date_clean",
    "dateclean":              "date_clean",
    # gkg_clean — nommage
    "GkgDate":                "gkg_date",
    "gkgdate":                "gkg_date",
    "GkgYearMonth":           "gkg_year_month",
    "gkgyearmonth":           "gkg_year_month",
    "GkgDatetime":            "gkg_datetime",
    "gkgdatetime":            "gkg_datetime",
    # Autres enrichies
    "ConfidenceLevel":        "confidence_level",
    "confidencelevel":        "confidence_level",
    "SourceLanguage":         "source_language",
    "sourcelanguage":         "source_language",
    "IsTranslated":           "is_translated",
    "istranslated":           "is_translated",
    "WordCount":              "word_count",
    "wordcount":              "word_count",
    "IsSignificant":          "is_significant",
    "issignificant":          "is_significant",
    "EventScope":             "event_scope",
    "eventscope":             "event_scope",
    "HasInternationalActor":  "has_international_actor",
    "hasinternationalactor":  "has_international_actor",
    "GoldsteinCategory":      "goldstein_category",
    "goldsteincategory":      "goldstein_category",
    "ToneCategory":           "tone_category",
    "tonecategory":           "tone_category",
    "InteractionType":        "interaction_type",
    "interactiontype":        "interaction_type",
    "IsRichArticle":          "is_rich_article",
    "isricharticle":          "is_rich_article",
}

# Enrichir avec ANTI_PATTERNS si disponible
if ANTI_PATTERNS:
    for ap in ANTI_PATTERNS:
        wrong = ap.get("wrong", "")
        correct = ap.get("correct", "")
        # Ne pas ajouter les patterns multi-mots ou alias (contiennent un '.')
        if wrong and correct and "." not in wrong and " " not in wrong:
            _COLUMN_NAME_CORRECTIONS[wrong] = correct


def _auto_correct_column_names(sql: str) -> Tuple[str, List[str]]:
    """
    Remplace les noms de colonnes erronés par leurs corrections connues.
    Retourne (sql_corrigé, liste_des_corrections_appliquées).
    
    Utilise des word boundaries pour éviter les faux positifs.
    """
    corrections_applied = []

    for wrong, correct in _COLUMN_NAME_CORRECTIONS.items():
        if wrong == correct:
            continue
        # Regex avec word boundaries, case-insensitive pour les noms sans casse
        pattern = re.compile(r'\b' + re.escape(wrong) + r'\b')
        if pattern.search(sql):
            sql = pattern.sub(correct, sql)
            corrections_applied.append(f"{wrong} → {correct}")

    return sql, corrections_applied


def _auto_correct_alias_errors(sql: str) -> Tuple[str, List[str]]:
    """
    Corrige les erreurs d'alias fréquentes :
    - m.EventCategory → e.EventCategory (colonne events_clean référencée avec alias mentions)
    - e.MentionDocTone → m.MentionDocTone (colonne mentions_clean référencée avec alias events)
    """
    corrections_applied = []
    schema = _get_schema()

    # Mapping des colonnes exclusives à chaque table
    events_only = schema.get("events_clean", set()) - schema.get("mentions_clean", set())
    mentions_only = schema.get("mentions_clean", set()) - schema.get("events_clean", set())

    # Corriger m.colonne_events → e.colonne_events
    for col in events_only:
        pattern = re.compile(r'\bm\.' + re.escape(col) + r'\b')
        if pattern.search(sql):
            sql = pattern.sub(f"e.{col}", sql)
            corrections_applied.append(f"m.{col} → e.{col}")

    # Corriger e.colonne_mentions → m.colonne_mentions
    for col in mentions_only:
        pattern = re.compile(r'\be\.' + re.escape(col) + r'\b')
        if pattern.search(sql):
            sql = pattern.sub(f"m.{col}", sql)
            corrections_applied.append(f"e.{col} → m.{col}")

    return sql, corrections_applied


def auto_correct_sql(sql: str) -> Tuple[str, List[str]]:
    """
    Pipeline complet d'auto-correction :
    1. Correction des noms de colonnes (CamelCase → snake_case)
    2. Correction des alias (m.col_events → e.col_events)
    
    Retourne (sql_corrigé, liste_de_toutes_les_corrections).
    """
    all_corrections = []

    sql, corr1 = _auto_correct_column_names(sql)
    all_corrections.extend(corr1)

    sql, corr2 = _auto_correct_alias_errors(sql)
    all_corrections.extend(corr2)

    return sql, all_corrections


# ════════════════════════════════════════════════════════════════
# VÉRIFICATIONS DE SÉCURITÉ
# ════════════════════════════════════════════════════════════════

def _contains_forbidden_keywords(sql: str) -> bool:
    upper = sql.upper()
    return any(re.search(rf"\b{kw}\b", upper) for kw in FORBIDDEN_KEYWORDS)


def _is_select_statement(sql: str) -> bool:
    upper = sql.strip().upper()
    return upper.startswith("SELECT") or upper.startswith("WITH")


def _extract_tables(sql: str) -> List[str]:
    """Extrait les tables BigQuery fully qualified (backtick-enclosed)."""
    pattern = r"`([^`]+\.[^`]+\.[^`]+)`"
    matches = re.findall(pattern, sql)
    return list(dict.fromkeys(matches))


def _contains_dangerous_wildcard(sql: str) -> bool:
    upper = sql.upper()
    return bool(re.search(r"\bSELECT\s+\*", upper))


def _has_time_filter(sql: str) -> bool:
    """Vérifie la présence d'au moins une référence temporelle (case-insensitive)."""
    return any(re.search(p, sql, re.IGNORECASE) for p in TIME_FILTER_PATTERNS)


def _resolve_allowed_tables(
    expected_tables: Optional[List[str]] = None,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
) -> Set[str]:
    if project and dataset and expected_tables:
        return {f"{project}.{dataset}.{t}" for t in expected_tables}
    return DEFAULT_ALLOWED_TABLES


# ════════════════════════════════════════════════════════════════
# EXTRACTION ET VALIDATION DES ALIAS / COLONNES
# ════════════════════════════════════════════════════════════════

def _extract_table_aliases(sql: str) -> Dict[str, str]:
    """
    Extrait les alias des tables depuis FROM/JOIN.
    
    Supporte :
    - FROM `project.dataset.table` alias
    - FROM `project.dataset.table` AS alias
    - JOIN `project.dataset.table` alias
    
    Retour : {"e": "events_clean", "m": "mentions_clean", ...}
    """
    alias_map: Dict[str, str] = {}
    pattern = re.compile(
        r"\b(?:FROM|JOIN)\s+`[^`]+\.(events_clean|mentions_clean|gkg_clean)`"
        r"(?:\s+AS)?\s+(\w+)",
        re.IGNORECASE,
    )
    for match in pattern.finditer(sql):
        table_name = match.group(1)
        alias = match.group(2).lower()
        # Éviter de capturer des mots-clés SQL comme alias
        if alias.upper() not in SQL_FUNCTIONS_AND_KEYWORDS:
            alias_map[alias] = table_name
    return alias_map


def _extract_unnest_aliases(sql: str) -> Set[str]:
    """
    Extrait les alias créés par UNNEST(SPLIT(...)).
    
    Exemples détectés :
    - UNNEST(SPLIT(V2Themes, ';')) AS theme → {"theme"}
    - , UNNEST(SPLIT(V2Persons, ';')) AS person → {"person"}
    """
    aliases = set()
    pattern = re.compile(r"UNNEST\s*\([^)]+\)\s+(?:AS\s+)?(\w+)", re.IGNORECASE)
    for match in pattern.finditer(sql):
        aliases.add(match.group(1).lower())
    return aliases


def _suggest_column(wrong_col: str, table_name: str) -> Optional[str]:
    """
    Suggère la colonne la plus proche dans le schéma de la table.
    Utilise une correspondance floue (difflib).
    """
    schema = _get_schema()
    valid_cols = schema.get(table_name, set())
    if not valid_cols:
        return None

    # Essai 1 : correspondance case-insensitive exacte
    col_lower_map = {c.lower(): c for c in valid_cols}
    if wrong_col.lower() in col_lower_map:
        return col_lower_map[wrong_col.lower()]

    # Essai 2 : correspondance floue
    matches = get_close_matches(
        wrong_col.lower(),
        [c.lower() for c in valid_cols],
        n=1,
        cutoff=0.6,
    )
    if matches:
        return col_lower_map.get(matches[0], matches[0])

    return None


def _validate_columns_against_schema(sql: str) -> None:
    """
    Vérifie que chaque alias.colonne référence une colonne réelle
    de la table correspondante.
    
    Gère :
    - Les alias de tables (e, m, g, etc.)
    - Les alias UNNEST (theme, person, org, etc.)
    - Les fonctions SQL qui ressemblent à alias.colonne
    - Les suggestions de correction en cas d'erreur
    """
    schema = _get_schema()
    alias_map = _extract_table_aliases(sql)
    unnest_aliases = _extract_unnest_aliases(sql)

    if not alias_map:
        return

    # Trouver toutes les références alias.colonne
    column_refs = re.findall(r"\b(\w+)\.(\w+)\b", sql)

    for alias_raw, column in column_refs:
        alias = alias_raw.lower()

        # Ignorer si l'alias est un alias UNNEST
        if alias in unnest_aliases or alias in UNNEST_ALIASES:
            continue

        # Ignorer si l'alias n'est pas une table connue
        if alias not in alias_map:
            continue

        # Ignorer les fonctions SQL (e.g., après FROM/JOIN le mot-clé)
        if column.upper() in SQL_FUNCTIONS_AND_KEYWORDS:
            continue

        # Ignorer les références BigQuery (project.dataset.table)
        if alias in ("gdelt", "benin_2025", "gdelt-494812"):
            continue

        table_name = alias_map[alias]
        allowed_columns = schema.get(table_name, set())

        if column not in allowed_columns:
            # Essayer la correction case-insensitive
            col_lower_map = {c.lower(): c for c in allowed_columns}
            if column.lower() in col_lower_map:
                # La colonne existe avec une casse différente — pas une erreur bloquante
                continue

            # Chercher dans l'autre table (erreur d'alias probable)
            other_tables = [t for t in schema if t != table_name]
            found_in_other = None
            for other_table in other_tables:
                other_cols = schema.get(other_table, set())
                other_lower = {c.lower(): c for c in other_cols}
                if column.lower() in other_lower:
                    found_in_other = other_table
                    break

            # Construire un message d'erreur utile
            suggestion = _suggest_column(column, table_name)
            error_parts = [
                f"Colonne inconnue détectée : {alias_raw}.{column} "
                f"(table réelle : {table_name})."
            ]

            if found_in_other:
                # Trouver le bon alias pour l'autre table
                correct_alias = next(
                    (a for a, t in alias_map.items() if t == found_in_other),
                    found_in_other
                )
                error_parts.append(
                    f"Cette colonne existe dans {found_in_other}. "
                    f"Utilisez {correct_alias}.{column} au lieu de {alias_raw}.{column}."
                )
            elif suggestion:
                error_parts.append(
                    f"Vouliez-vous dire {alias_raw}.{suggestion} ?"
                )

            raise SQLValidationException(" ".join(error_parts))


# ════════════════════════════════════════════════════════════════
# VALIDATION PRINCIPALE
# ════════════════════════════════════════════════════════════════

def validate_sql(
    sql: str,
    expected_tables: Optional[List[str]] = None,
    project: Optional[str] = None,
    dataset: Optional[str] = None,
    require_time_filter: bool = True,
    allow_select_star: bool = False,
    validate_columns: bool = True,
    auto_correct: bool = True,
) -> str:
    """
    Valide et (optionnellement) auto-corrige une requête SQL générée par le LLM.
    
    Pipeline :
    1. Normalise le SQL
    2. Auto-corrige les erreurs connues (si auto_correct=True)
    3. Vérifie la sécurité (mots-clés interdits, tables autorisées)
    4. Vérifie la structure (SELECT/WITH, pas de SELECT *)
    5. Vérifie le filtre temporel
    6. Vérifie les alias.colonnes contre le schéma
    
    Retourne le SQL validé (et potentiellement corrigé).
    Lève SQLValidationException en cas d'erreur non corrigeable.
    
    Args:
        sql: La requête SQL à valider
        expected_tables: Tables attendues (surcharge la whitelist par défaut)
        project: Projet BigQuery (pour construire les noms fully qualified)
        dataset: Dataset BigQuery
        require_time_filter: Exiger un filtre temporel (défaut True)
        allow_select_star: Autoriser SELECT * (défaut False)
        validate_columns: Valider les alias.colonnes (défaut True)
        auto_correct: Auto-corriger les erreurs connues (défaut True)
    
    Returns:
        str: Le SQL validé et potentiellement corrigé
    
    Raises:
        SQLValidationException: Si le SQL contient une erreur non corrigeable
    """
    # ─── 1. Normalisation ───
    normalized_sql = _normalize_sql(sql)

    if not normalized_sql:
        raise SQLValidationException("La requête SQL est vide.")

    # ─── 2. Auto-correction (avant toute validation) ───
    corrections = []
    if auto_correct:
        normalized_sql, corrections = auto_correct_sql(normalized_sql)

    # ─── 3. Structure de base ───
    if not _is_select_statement(normalized_sql):
        raise SQLValidationException(
            "La requête doit commencer par SELECT ou WITH."
        )

    # ─── 4. Mots-clés dangereux ───
    if _contains_forbidden_keywords(normalized_sql):
        raise SQLValidationException(
            "La requête contient des mots-clés SQL interdits "
            "(INSERT, UPDATE, DELETE, DROP, ALTER, etc.)."
        )

    # ─── 5. SELECT * ───
    if not allow_select_star and _contains_dangerous_wildcard(normalized_sql):
        raise SQLValidationException(
            "L'usage de SELECT * est interdit. "
            "Sélectionnez explicitement les colonnes nécessaires."
        )

    # ─── 6. Tables autorisées ───
    tables_found = _extract_tables(normalized_sql)

    if not tables_found:
        raise SQLValidationException(
            "Aucune table BigQuery fully qualified n'a été détectée. "
            "Utilisez le format `project.dataset.table`."
        )

    allowed_tables = _resolve_allowed_tables(
        expected_tables=expected_tables,
        project=project,
        dataset=dataset,
    )

    unauthorized = [t for t in tables_found if t not in allowed_tables]
    if unauthorized:
        raise SQLValidationException(
            f"Table(s) non autorisée(s) : {unauthorized}. "
            f"Tables autorisées : {sorted(allowed_tables)}."
        )

    # ─── 7. Filtre temporel ───
    if require_time_filter and not _has_time_filter(normalized_sql):
        raise SQLValidationException(
            "La requête doit contenir un filtre temporel "
            "(ex: Year = 2025, year_month_clean, mention_year_month, "
            "gkg_year_month, date_clean, etc.)."
        )

    # ─── 8. Validation des colonnes contre le schéma ───
    if validate_columns:
        _validate_columns_against_schema(normalized_sql)

    return normalized_sql