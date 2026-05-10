# assistant/metadata/schema_retriever.py
# ================================================================
# GDELT BÉNIN 2025 — Schema Retriever v2.0
# ================================================================
# Récupère les descriptions métier des colonnes pertinentes
# pour une question utilisateur, avec scoring enrichi.
#
# v2.0 :
#   - Scoring élargi (definition, use_for, filters_hint)
#   - Détection automatique des tables pertinentes
#   - Injection du contexte de jointure si multi-tables
#   - Injection des anti-patterns spécifiques aux colonnes matchées
#   - Utilisation de TABLE_METADATA pour le contexte structurel
# ================================================================

import re
from typing import Dict, List, Optional, Set, Tuple

from assistant.metadata.column_dictionary import COLUMN_METADATA

# Imports enrichis v2 (avec fallback)
try:
    from assistant.metadata.column_dictionary import (
        TABLE_METADATA,
        TABLE_RELATIONSHIPS,
        NAMING_RULES,
        ANTI_PATTERNS,
        VALID_COLUMNS,
    )
except ImportError:
    TABLE_METADATA = {}
    TABLE_RELATIONSHIPS = {}
    NAMING_RULES = ""
    ANTI_PATTERNS = []
    VALID_COLUMNS = {}


# ════════════════════════════════════════════════════════════════
# DÉTECTION AUTOMATIQUE DES TABLES PERTINENTES
# ════════════════════════════════════════════════════════════════

# Mots-clés associés à chaque table
_TABLE_KEYWORDS: Dict[str, List[str]] = {
    "events_clean": [
        "événement", "evenement", "event", "conflit", "coopération",
        "cooperation", "acteur", "actor", "goldstein", "gravité",
        "gravite", "géographique", "geographique", "lieu", "zone",
        "département", "departement", "significatif", "international",
        "local", "portée", "scope", "quadclass", "interaction",
    ],
    "mentions_clean": [
        "mention", "couverture", "média", "media", "source",
        "médiatique", "mediatique", "confiance", "confidence",
        "tonalité mention", "ton mention", "langue", "traduit",
        "translation", "broadcast", "newspaper", "web",
    ],
    "gkg_clean": [
        "article", "thème", "theme", "personne", "person",
        "organisation", "organization", "gkg", "knowledge graph",
        "publication", "éditeur", "editeur", "mot", "word",
        "riche", "rich", "v2themes", "v2persons", "v2organizations",
        "tonalité article", "polarité", "polarity",
    ],
}


def _detect_relevant_tables(user_question: str) -> List[str]:
    """
    Détecte quelles tables sont probablement pertinentes
    en analysant les mots-clés de la question.
    Retourne les tables triées par pertinence.
    """
    q = user_question.lower()
    scores: Dict[str, int] = {}

    for table, keywords in _TABLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in q)
        if score > 0:
            scores[table] = score

    if not scores:
        # Fallback : toutes les tables
        return list(COLUMN_METADATA.keys())

    # Trier par score décroissant
    sorted_tables = sorted(scores.keys(), key=lambda t: scores[t], reverse=True)
    return sorted_tables


# ════════════════════════════════════════════════════════════════
# SCORING DES COLONNES (enrichi v2)
# ════════════════════════════════════════════════════════════════

def _score_column(
    col_name: str,
    desc: Dict,
    question_lower: str,
) -> int:
    """
    Calcule un score de pertinence pour une colonne donnée
    par rapport à la question utilisateur.

    Scoring :
    - synonyms match       → +3 (le plus fiable)
    - business_name match  → +2
    - use_for match        → +2
    - definition match     → +1
    - filters_hint match   → +1
    - col_name match       → +1
    """
    score = 0

    # 1. Synonyms (poids fort)
    for syn in desc.get("synonyms", []):
        if syn.lower() in question_lower:
            score += 3
            break

    # 2. Business name (poids moyen)
    bname = desc.get("business_name", "").lower()
    if bname and bname in question_lower:
        score += 2

    # 3. Use_for (poids moyen — matche les cas d'usage)
    for use in desc.get("use_for", []):
        use_words = use.lower().split()
        matching = sum(1 for w in use_words if len(w) > 3 and w in question_lower)
        if matching >= 2:
            score += 2
            break

    # 4. Definition (poids faible — matche les termes métier)
    definition = desc.get("definition", "").lower()
    def_words = re.findall(r'\b\w{4,}\b', question_lower)
    def_matches = sum(1 for w in def_words if w in definition)
    if def_matches >= 2:
        score += 1

    # 5. Filters_hint (poids faible)
    filters = desc.get("filters_hint", "").lower()
    if any(w in filters for w in def_words if len(w) > 4):
        score += 1

    # 6. Nom de colonne brut (poids faible)
    if col_name.lower() in question_lower:
        score += 1

    return score


# ════════════════════════════════════════════════════════════════
# CONTEXTE DE JOINTURE
# ════════════════════════════════════════════════════════════════

def _get_join_context(matched_tables: Set[str]) -> str:
    """
    Si la question implique plusieurs tables, injecte le contexte
    de jointure (autorisée ou interdite).
    """
    if len(matched_tables) < 2 or not TABLE_RELATIONSHIPS:
        return ""

    lines = ["\n🔗 CONTEXTE DE JOINTURE :"]

    # Jointures autorisées
    for join in TABLE_RELATIONSHIPS.get("allowed_joins", []):
        left = join.get("left_table", "")
        right = join.get("right_table", "")
        if left in matched_tables and right in matched_tables:
            pattern = join.get("sql_pattern", "")
            lines.append(f"  ✅ AUTORISÉE : {left} ↔ {right}")
            lines.append(f"     Pattern : {pattern}")
            aliases = join.get("standard_aliases", {})
            if aliases:
                lines.append(f"     Alias : {aliases}")

    # Jointures interdites
    for forbidden in TABLE_RELATIONSHIPS.get("forbidden_joins", []):
        tables = forbidden.get("tables", [])
        if len(tables) == 2 and set(tables).issubset(matched_tables):
            reason = forbidden.get("reason", "")
            lines.append(f"  ❌ INTERDITE : {tables[0]} ↔ {tables[1]}")
            lines.append(f"     Raison : {reason}")

    # Column ownership (rappel alias)
    ownership = TABLE_RELATIONSHIPS.get("column_ownership", {})
    if ownership and ownership.get("notes"):
        lines.append(f"  ⚠️  {ownership['notes']}")

    return "\n".join(lines) if len(lines) > 1 else ""


# ════════════════════════════════════════════════════════════════
# ANTI-PATTERNS SPÉCIFIQUES AUX COLONNES MATCHÉES
# ════════════════════════════════════════════════════════════════

def _get_relevant_anti_patterns(matched_columns: Set[str]) -> str:
    """
    Retourne les anti-patterns qui concernent les colonnes matchées.
    """
    if not ANTI_PATTERNS or not matched_columns:
        return ""

    relevant = []
    matched_lower = {c.lower() for c in matched_columns}

    for ap in ANTI_PATTERNS:
        wrong = ap.get("wrong", "")
        correct = ap.get("correct", "")

        # Vérifier si le correct ou le wrong concerne une colonne matchée
        wrong_base = wrong.split(".")[-1].lower() if "." in wrong else wrong.lower()
        correct_base = correct.split(".")[-1].lower() if "." in correct else correct.lower()

        if wrong_base in matched_lower or correct_base in matched_lower:
            relevant.append(ap)

    if not relevant:
        return ""

    lines = ["\n⚠️  PIÈGES SPÉCIFIQUES AUX COLONNES CI-DESSUS :"]
    for ap in relevant[:10]:  # Limiter à 10 pour ne pas surcharger
        wrong = ap.get("wrong", "")
        correct = ap.get("correct", "")
        explanation = ap.get("explanation", "")
        lines.append(f"  ✗ {wrong}  →  ✓ {correct}")
        if explanation:
            lines.append(f"    {explanation}")

    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# TABLE METADATA BLOCK
# ════════════════════════════════════════════════════════════════

def _get_table_context(table: str) -> str:
    """
    Retourne le contexte structurel de la table depuis TABLE_METADATA.
    """
    if not TABLE_METADATA:
        return ""

    meta = TABLE_METADATA.get(table, {})
    if not meta:
        return ""

    grain = meta.get("grain", "")
    temporal_filter = meta.get("temporal_filter", "")
    temporal_daily = meta.get("temporal_column_daily", "")
    temporal_monthly = meta.get("temporal_column_monthly", "")

    parts = [f"  📋 Grain : {grain}"]
    if temporal_filter:
        parts.append(f"  🕐 Filtre temporel : {temporal_filter}")
    if temporal_daily:
        parts.append(f"  📅 Colonne journalière : {temporal_daily}")
    if temporal_monthly:
        parts.append(f"  📆 Colonne mensuelle : {temporal_monthly}")

    return "\n".join(parts)


# ════════════════════════════════════════════════════════════════
# FONCTION PRINCIPALE — get_relevant_column_descriptions
# ════════════════════════════════════════════════════════════════

def get_relevant_column_descriptions(
    user_question: str,
    tables: Optional[List[str]] = None,
    max_per_table: int = 8,
) -> str:
    """
    Retourne un bloc texte avec les descriptions des colonnes
    les plus pertinentes pour la question utilisateur.

    v2.0 améliorations :
    - Scoring enrichi (definition, use_for, filters_hint)
    - Détection automatique des tables pertinentes
    - Contexte de jointure si multi-tables
    - Anti-patterns spécifiques aux colonnes matchées
    - Contexte structurel de chaque table (grain, filtre temporel)
    """
    q = user_question.lower()

    # Déterminer les tables cibles
    if tables:
        target_tables = tables
    else:
        target_tables = _detect_relevant_tables(user_question)

    blocks = []
    all_matched_columns: Set[str] = set()
    matched_tables: Set[str] = set()

    for table in target_tables:
        meta = COLUMN_METADATA.get(table, {})
        matched = []

        for col_name, desc in meta.items():
            score = _score_column(col_name, desc, q)
            if score > 0:
                matched.append((score, col_name, desc))

        # Trier par score décroissant, garder les top
        matched.sort(key=lambda x: x[0], reverse=True)
        matched = matched[:max_per_table]

        if matched:
            matched_tables.add(table)

            # En-tête de table avec contexte structurel
            lines = [f"\n--- COLONNES PERTINENTES : {table} ---"]

            # Ajouter le contexte de la table
            table_ctx = _get_table_context(table)
            if table_ctx:
                lines.append(table_ctx)

            for _, col_name, desc in matched:
                all_matched_columns.add(col_name)

                origin_tag = "[ENRICHI]" if desc.get("origin") == "enriched" else "[GDELT]"
                use_for = " | ".join(desc.get("use_for", []))
                avoid_for = " | ".join(desc.get("avoid_for", []))
                agg = desc.get("aggregation_hint", "")
                notes = desc.get("notes", "")
                join_role = desc.get("join_role", "")
                filters = desc.get("filters_hint", "")

                block = (
                    f"\n{origin_tag} {table}.{col_name} — {desc['business_name']}\n"
                    f"  Définition : {desc['definition']}\n"
                    f"  ✅ UTILISER POUR : {use_for}\n"
                    f"  ❌ NE PAS UTILISER POUR : {avoid_for}\n"
                    f"  📊 Agrégation : {agg}\n"
                )
                if filters:
                    block += f"  🔍 Filtre : {filters}\n"
                if notes:
                    block += f"  ⚠️  PIÈGE : {notes}\n"
                if join_role and join_role != "Aucun." and join_role != "Aucun":
                    block += f"  🔗 Jointure : {join_role}\n"

                lines.append(block)
            blocks.append("\n".join(lines))

    # Ajouter le contexte de jointure si multi-tables
    join_ctx = _get_join_context(matched_tables)
    if join_ctx:
        blocks.append(join_ctx)

    # Ajouter les anti-patterns spécifiques
    ap_block = _get_relevant_anti_patterns(all_matched_columns)
    if ap_block:
        blocks.append(ap_block)

    return "\n".join(blocks) if blocks else ""


# ════════════════════════════════════════════════════════════════
# FALLBACK COMPACT
# ════════════════════════════════════════════════════════════════

def get_all_column_descriptions_compact(
    tables: Optional[List[str]] = None,
) -> str:
    """
    Version compacte : liste toutes les colonnes avec
    business_name + définition courte + origin.
    Utilisée comme fallback si aucun match de synonyme.

    v2.0 : ajoute le contexte structurel de chaque table.
    """
    target_tables = tables if tables else list(COLUMN_METADATA.keys())
    lines = []

    for table in target_tables:
        meta = COLUMN_METADATA.get(table, {})

        # En-tête avec contexte structurel
        lines.append(f"\n=== {table} ===")

        # Contexte de la table
        if TABLE_METADATA:
            tmeta = TABLE_METADATA.get(table, {})
            grain = tmeta.get("grain", "")
            temporal = tmeta.get("temporal_filter", "")
            if grain:
                lines.append(f"  Grain : {grain}")
            if temporal:
                lines.append(f"  Filtre : {temporal}")

            # Key metrics et dimensions
            key_metrics = tmeta.get("key_metrics", [])
            key_dims = tmeta.get("key_dimensions", [])
            if key_metrics:
                lines.append(f"  Métriques clés : {', '.join(key_metrics)}")
            if key_dims:
                lines.append(f"  Dimensions clés : {', '.join(key_dims)}")

        # Colonnes
        for col_name, desc in meta.items():
            origin_tag = "[E]" if desc.get("origin") == "enriched" else "[G]"
            definition_short = desc.get("definition", "")[:90]
            lines.append(
                f"  {origin_tag} {col_name} : {desc['business_name']} "
                f"— {definition_short}..."
            )

    return "\n".join(lines)