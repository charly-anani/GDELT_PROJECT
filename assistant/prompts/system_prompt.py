# assistant/prompts/system_prompt.py
# ================================================================
# GDELT BÉNIN 2025 — System Prompt v2.0
# ================================================================
# Optimisé pour NL2SQL avec grounding complet :
#   - Noms de colonnes EXACTS (snake_case vs CamelCase)
#   - NAMING_RULES injectées depuis column_dictionary
#   - ANTI_PATTERNS injectés comme garde-fous
#   - COMMON_QUERY_PATTERNS injectés comme few-shot examples
#   - TABLE_METADATA pour le contexte structurel
# ================================================================

from assistant.core.config import BQ_PROJECT, BQ_DATASET, ALLOWED_INTENTS
from assistant.metadata.schema_retriever import (
    get_relevant_column_descriptions,
    get_all_column_descriptions_compact,
)

# ── Imports depuis column_dictionary v2 ──
try:
    from assistant.metadata.column_dictionary import (
        NAMING_RULES,
        ANTI_PATTERNS,
        COMMON_QUERY_PATTERNS,
        TABLE_METADATA,
        TABLE_RELATIONSHIPS,
        VALID_COLUMNS,
    )
except ImportError:
    NAMING_RULES = ""
    ANTI_PATTERNS = []
    COMMON_QUERY_PATTERNS = {}
    TABLE_METADATA = {}
    TABLE_RELATIONSHIPS = {}
    VALID_COLUMNS = {}


# ════════════════════════════════════════════════════════════════
# HELPERS — Construction dynamique des blocs de prompt
# ════════════════════════════════════════════════════════════════

def _build_anti_patterns_block() -> str:
    """
    Construit le bloc d'anti-patterns à injecter dans le prompt.
    Sélectionne les plus critiques pour ne pas surcharger le contexte.
    """
    if not ANTI_PATTERNS:
        return ""

    lines = ["ERREURS FRÉQUENTES À ÉVITER ABSOLUMENT :"]
    for ap in ANTI_PATTERNS:
        wrong = ap.get("wrong", "")
        correct = ap.get("correct", "")
        explanation = ap.get("explanation", "")
        if wrong and correct:
            lines.append(f"  ✗ {wrong}  →  ✓ {correct}")
            if explanation:
                lines.append(f"    Raison : {explanation}")
    return "\n".join(lines)


def _build_valid_columns_block() -> str:
    """
    Construit la liste complète des colonnes valides par table.
    """
    if not VALID_COLUMNS:
        return ""

    lines = ["COLONNES VALIDES PAR TABLE (NE JAMAIS INVENTER D'AUTRES COLONNES) :"]
    for table, cols in VALID_COLUMNS.items():
        cols_str = ", ".join(cols)
        lines.append(f"\n  {table} ({len(cols)} colonnes) :")
        lines.append(f"    {cols_str}")
    return "\n".join(lines)


def _build_query_patterns_block(user_question: str) -> str:
    """
    Sélectionne les 3-5 patterns SQL les plus pertinents pour la question.
    Utilise un matching simple par mots-clés sur question_types.
    """
    if not COMMON_QUERY_PATTERNS or not user_question:
        return ""

    question_lower = user_question.lower()
    scored_patterns = []

    for key, pattern in COMMON_QUERY_PATTERNS.items():
        score = 0
        question_types = pattern.get("question_types", [])
        for qt in question_types:
            # Compter les mots de qt présents dans la question
            words = qt.lower().split()
            matching_words = sum(1 for w in words if w in question_lower)
            if matching_words > 0:
                score = max(score, matching_words / len(words))
        if score > 0:
            scored_patterns.append((score, key, pattern))

    # Trier par pertinence et prendre les top 5
    scored_patterns.sort(key=lambda x: x[0], reverse=True)
    top_patterns = scored_patterns[:5]

    if not top_patterns:
        return ""

    lines = ["PATTERNS SQL DE RÉFÉRENCE (adapte-les à la question, ne copie pas aveuglément) :"]
    for _, key, pattern in top_patterns:
        desc = pattern.get("description", key)
        sql = pattern.get("sql_template", "").strip()
        notes = pattern.get("notes", "")
        lines.append(f"\n--- {desc} ---")
        lines.append(sql)
        if notes:
            lines.append(f"Note : {notes}")

    return "\n".join(lines)


# ════════════════════════════════════════════════════════════════
# PROMPT STATIQUE — Corrigé avec les vrais noms de colonnes
# ════════════════════════════════════════════════════════════════

_STATIC_PROMPT = f"""Réponds UNIQUEMENT avec un objet JSON valide. Pas de texte. Pas de markdown. Pas de ```.

FORMAT OBLIGATOIRE :
{{"intent":"<intent>","tables":["<t>"],"sql":"SELECT ...","chart_recommendation":"<type>","explanation_hint":"<phrase courte>"}}

PROJET : {BQ_PROJECT}
DATASET : {BQ_DATASET}
PÉRIMÈTRE : Bénin 2025

═══════════════════════════════════════════════
TABLES DISPONIBLES — NOMS DE COLONNES EXACTS
═══════════════════════════════════════════════

events_clean (39 colonnes) — Un événement géopolitique par ligne :
  Clé primaire     : GLOBALEVENTID
  Dates            : Year (INT), date_clean (DATE 'YYYY-MM-DD'), year_month_clean (STRING 'YYYY-MM')
  Dates brutes     : SQLDATE, DATEADDED, MonthYear (NE PAS utiliser pour analyses métier)
  Acteurs          : Actor1Name, Actor2Name, Actor1CountryCode, Actor2CountryCode
  Types acteurs    : Actor1Type1Code, Actor2Type1Code, Actor1Role, Actor2Role
  Codes événement  : EventCode, EventBaseCode, EventRootCode, QuadClass
  Labels enrichis  : EventCategory, QuadClass_Label, interaction_type
  Métriques        : GoldsteinScale, AvgTone, NumMentions, NumSources, NumArticles
  Géographie       : ActionGeo_FullName, ActionGeo_CountryCode, ActionGeo_ADM1Code, ActionGeo_Lat, ActionGeo_Long
  Drapeaux         : is_significant (BOOLEAN), has_international_actor (BOOLEAN), IsRootEvent
  Catégories       : goldstein_category, tone_category, event_scope
  URL              : SOURCEURL

mentions_clean (15 colonnes) — Une mention médiatique par ligne :
  Clé jointure     : GLOBALEVENTID
  Dates            : mention_date (DATE), mention_year_month (STRING 'YYYY-MM'), mention_datetime (TIMESTAMP)
  Date brute       : MentionTimeDate (INT brut — NE PAS utiliser pour analyses)
  Source           : MentionSourceName, MentionType (INT brut), MentionType_Label (STRING lisible)
  Métriques        : MentionDocTone (FLOAT), Confidence (INT 0-100)
  Enrichis         : tone_category, confidence_level, source_language, is_translated
  Traduction brute : MentionDocTranslationInfo (NE PAS utiliser — préférer source_language et is_translated)

gkg_clean (28 colonnes) — Un article de presse par ligne :
  Clé              : GKGRECORDID
  Dates            : gkg_date (DATE), gkg_year_month (STRING 'YYYY-MM'), gkg_datetime (TIMESTAMP)
  Date brute       : DATE (INT brut — NE PAS utiliser pour analyses)
  Source           : SourceCommonName, DocumentIdentifier
  Tonalité         : tone (FLOAT global), tone_positive, tone_negative, tone_polarity, tone_activity
  Compteurs        : word_count, nb_themes, nb_persons, nb_organizations, nb_locations
  Multi-valeurs    : V2Themes, V2Persons, V2Organizations, V2Locations (TOUJOURS utiliser UNNEST)
  Enrichis         : tone_category, source_language, is_translated, is_rich_article
  Bruts inutiles   : V2Tone, TranslationInfo, SharingImage

═══════════════════════════════════════════════
RÈGLES SQL CRITIQUES
═══════════════════════════════════════════════

1. SQL SELECT uniquement. Jamais INSERT, UPDATE, DELETE, DROP, ALTER, CREATE.

2. Tables fully-qualified OBLIGATOIRES :
   `{BQ_PROJECT}.{BQ_DATASET}.events_clean`
   `{BQ_PROJECT}.{BQ_DATASET}.mentions_clean`
   `{BQ_PROJECT}.{BQ_DATASET}.gkg_clean`

3. JOINTURE : uniquement events_clean ↔ mentions_clean sur GLOBALEVENTID :
   `{BQ_PROJECT}.{BQ_DATASET}.events_clean` e
   JOIN `{BQ_PROJECT}.{BQ_DATASET}.mentions_clean` m
   ON e.GLOBALEVENTID = m.GLOBALEVENTID

4. JOINTURE INTERDITE : gkg_clean ne peut PAS être jointe aux autres tables.

5. NE JAMAIS inventer de colonnes. Utilise UNIQUEMENT les colonnes listées ci-dessus.

6. ALIAS STANDARD : events_clean → e, mentions_clean → m

7. Quand tu utilises un alias, VÉRIFIE que la colonne appartient à la bonne table :
   - e.EventCategory ✓   (EventCategory est dans events_clean)
   - m.EventCategory ✗   (EventCategory N'EST PAS dans mentions_clean)
   - m.MentionDocTone ✓  (MentionDocTone est dans mentions_clean)
   - e.MentionDocTone ✗  (MentionDocTone N'EST PAS dans events_clean)
   - e.is_significant ✓  (is_significant est dans events_clean)
   - m.is_significant ✗  (is_significant N'EST PAS dans mentions_clean)
   - e.year_month_clean ✓ (year_month_clean est dans events_clean)
   - m.year_month_clean ✗ (year_month_clean N'EST PAS dans mentions_clean → utiliser m.mention_year_month)

═══════════════════════════════════════════════
NOMMAGE DES COLONNES — RÈGLE CRITIQUE
═══════════════════════════════════════════════

Les colonnes GDELT natives sont en CamelCase : GoldsteinScale, AvgTone, MentionDocTone, MentionSourceName...
Les colonnes ENRICHIES sont en snake_case : date_clean, year_month_clean, mention_date, mention_year_month, gkg_date, gkg_year_month, is_significant, event_scope, tone_category, confidence_level...
EXCEPTIONS (enrichies mais style mixte) : QuadClass_Label, EventCategory, Actor1Role, Actor2Role, MentionType_Label

NE JAMAIS ÉCRIRE :
  ✗ MentionYearMonth    → ✓ mention_year_month
  ✗ DateClean           → ✓ date_clean
  ✗ YearMonthClean      → ✓ year_month_clean
  ✗ GkgDate             → ✓ gkg_date
  ✗ GkgYearMonth        → ✓ gkg_year_month
  ✗ IsSignificant       → ✓ is_significant
  ✗ EventScope          → ✓ event_scope
  ✗ WordCount           → ✓ word_count
  ✗ ConfidenceLevel     → ✓ confidence_level

═══════════════════════════════════════════════
FILTRES TEMPORELS PAR TABLE
═══════════════════════════════════════════════

events_clean   → WHERE Year = 2025
mentions_clean → WHERE mention_year_month LIKE '2025-%'
gkg_clean      → WHERE gkg_year_month LIKE '2025-%'

═══════════════════════════════════════════════
COLONNES DE TONALITÉ — NE PAS CONFONDRE
═══════════════════════════════════════════════

events_clean   : AvgTone       → tonalité moyenne des articles couvrant l'événement
mentions_clean : MentionDocTone → tonalité du document source de la mention
gkg_clean      : tone          → tonalité globale de l'article GKG
TOUTES tables  : tone_category → catégorie enrichie ('Très négatif'...'Très positif')
NE PAS confondre : GoldsteinScale mesure la GRAVITÉ GÉOPOLITIQUE, PAS la tonalité médiatique.

═══════════════════════════════════════════════
RÈGLES GKG — CHAMPS MULTI-VALEURS
═══════════════════════════════════════════════

V2Themes, V2Persons, V2Organizations, V2Locations contiennent PLUSIEURS valeurs séparées par ';'.
TOUJOURS utiliser : UNNEST(SPLIT(colonne, ';')) AS alias WHERE alias != ''
JAMAIS sélectionner ces colonnes brutes pour compter.

Exemples :
  SELECT theme, COUNT(*) FROM `...gkg_clean`, UNNEST(SPLIT(V2Themes, ';')) AS theme WHERE theme != '' AND gkg_year_month LIKE '2025-%' GROUP BY theme
  SELECT person, COUNT(*) FROM `...gkg_clean`, UNNEST(SPLIT(V2Persons, ';')) AS person WHERE person != '' AND gkg_year_month LIKE '2025-%' GROUP BY person

═══════════════════════════════════════════════
CORRESPONDANCES MÉTIER → SQL
═══════════════════════════════════════════════

"couverture médiatique"      → COUNT(*) sur mentions_clean (PAS AVG(Confidence))
"top médias"                 → GROUP BY m.MentionSourceName ORDER BY COUNT(*) DESC
"tonalité des mentions"      → AVG(m.MentionDocTone)
"tonalité des événements"    → AVG(e.AvgTone)
"tonalité des articles"      → AVG(tone) dans gkg_clean
"événements significatifs"   → WHERE e.is_significant = TRUE
"acteurs internationaux"     → WHERE e.has_international_actor = TRUE
"évolution mensuelle events" → GROUP BY e.year_month_clean ORDER BY e.year_month_clean
"évolution mensuelle mentions" → GROUP BY m.mention_year_month ORDER BY m.mention_year_month
"évolution mensuelle articles" → GROUP BY gkg_year_month ORDER BY gkg_year_month
"thèmes fréquents"           → UNNEST(SPLIT(V2Themes, ';')) AS theme ... GROUP BY theme
"personnes citées"           → UNNEST(SPLIT(V2Persons, ';')) AS person ... GROUP BY person
"organisations citées"       → UNNEST(SPLIT(V2Organizations, ';')) AS org ... GROUP BY org
"par département"            → GROUP BY e.ActionGeo_FullName ou e.ActionGeo_ADM1Code
"coopération vs conflit"     → GROUP BY e.QuadClass_Label
"gravité"                    → AVG(e.GoldsteinScale), goldstein_category
"portée locale/internationale" → GROUP BY e.event_scope

═══════════════════════════════════════════════
INTENTS DISPONIBLES
═══════════════════════════════════════════════

{", ".join(ALLOWED_INTENTS)}

Si question ambiguë → intent = "clarification_needed", sql = ""
Si hors périmètre   → intent = "out_of_scope_question", sql = ""

═══════════════════════════════════════════════
CHART RECOMMENDATIONS
═══════════════════════════════════════════════

kpi   = une seule valeur agrégée
line  = série temporelle (évolution dans le temps)
bar   = classement, top, répartition par catégorie
map   = analyse géographique avec coordonnées
table = autre / résultat tabulaire

═══════════════════════════════════════════════
EXEMPLES CORRIGÉS
═══════════════════════════════════════════════

Q: "Combien d'événements au Bénin en 2025 ?"
{{"intent":"count_events","tables":["events_clean"],"sql":"SELECT COUNT(DISTINCT GLOBALEVENTID) AS total FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` WHERE Year = 2025","chart_recommendation":"kpi","explanation_hint":"Nombre total d'événements au Bénin en 2025."}}

Q: "Top 10 médias qui couvrent le plus les événements en 2025"
{{"intent":"top_sources","tables":["mentions_clean","events_clean"],"sql":"SELECT m.MentionSourceName, COUNT(*) AS total FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` e JOIN `{BQ_PROJECT}.{BQ_DATASET}.mentions_clean` m ON e.GLOBALEVENTID = m.GLOBALEVENTID WHERE e.Year = 2025 GROUP BY m.MentionSourceName ORDER BY total DESC LIMIT 10","chart_recommendation":"bar","explanation_hint":"Top 10 des médias par volume de mentions en 2025."}}

Q: "Évolution mensuelle de la tonalité des événements en 2025"
{{"intent":"trend_analysis","tables":["events_clean"],"sql":"SELECT year_month_clean, ROUND(AVG(AvgTone), 2) AS tonalite_moyenne FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` WHERE Year = 2025 GROUP BY year_month_clean ORDER BY year_month_clean","chart_recommendation":"line","explanation_hint":"Tonalité moyenne mensuelle des événements au Bénin en 2025."}}

Q: "Quels événements significatifs ont eu la plus forte couverture médiatique moyenne par mois ?"
{{"intent":"event_media_coverage","tables":["events_clean","mentions_clean"],"sql":"SELECT e.year_month_clean, e.EventCategory, COUNT(DISTINCT e.GLOBALEVENTID) AS nb_events, COUNT(*) AS total_mentions, ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT e.GLOBALEVENTID), 2) AS avg_mentions_per_event FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` e JOIN `{BQ_PROJECT}.{BQ_DATASET}.mentions_clean` m ON e.GLOBALEVENTID = m.GLOBALEVENTID WHERE e.Year = 2025 AND e.is_significant = TRUE GROUP BY e.year_month_clean, e.EventCategory ORDER BY avg_mentions_per_event DESC LIMIT 20","chart_recommendation":"bar","explanation_hint":"Événements significatifs par couverture médiatique moyenne mensuelle."}}

Q: "Quels sont les thèmes les plus fréquents dans les articles riches à tonalité négative ?"
{{"intent":"top_themes","tables":["gkg_clean"],"sql":"SELECT theme, COUNT(*) AS nb FROM `{BQ_PROJECT}.{BQ_DATASET}.gkg_clean`, UNNEST(SPLIT(V2Themes, ';')) AS theme WHERE theme != '' AND gkg_year_month LIKE '2025-%' AND tone < 0 AND is_rich_article = TRUE GROUP BY theme ORDER BY nb DESC LIMIT 20","chart_recommendation":"bar","explanation_hint":"Top thèmes dans les articles riches à tonalité négative."}}

Q: "Quelles sont les sources francophones qui couvrent le plus les conflits ?"
{{"intent":"top_sources","tables":["events_clean","mentions_clean"],"sql":"SELECT m.MentionSourceName, COUNT(*) AS nb_mentions, ROUND(AVG(m.MentionDocTone), 2) AS avg_tone FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` e JOIN `{BQ_PROJECT}.{BQ_DATASET}.mentions_clean` m ON e.GLOBALEVENTID = m.GLOBALEVENTID WHERE e.Year = 2025 AND e.QuadClass_Label IN ('Verbal Conflict', 'Material Conflict') AND m.source_language = 'fr' GROUP BY m.MentionSourceName ORDER BY nb_mentions DESC LIMIT 15","chart_recommendation":"bar","explanation_hint":"Top sources francophones couvrant les conflits au Bénin en 2025."}}

Q: "Répartition coopération vs conflit par mois"
{{"intent":"trend_analysis","tables":["events_clean"],"sql":"SELECT year_month_clean, QuadClass_Label, COUNT(DISTINCT GLOBALEVENTID) AS nb_events FROM `{BQ_PROJECT}.{BQ_DATASET}.events_clean` WHERE Year = 2025 GROUP BY year_month_clean, QuadClass_Label ORDER BY year_month_clean","chart_recommendation":"line","explanation_hint":"Évolution mensuelle coopération vs conflit au Bénin en 2025."}}
"""


# ════════════════════════════════════════════════════════════════
# BLOC DYNAMIQUE — Schéma contextuel
# ════════════════════════════════════════════════════════════════

def _build_dynamic_schema_block(user_question: str) -> str:
    """
    Injecte les colonnes métier les plus pertinentes pour la question.
    Fallback compact si aucun match.
    """
    if not user_question or not user_question.strip():
        compact = get_all_column_descriptions_compact(
            tables=["events_clean", "mentions_clean", "gkg_clean"]
        )
        return f"""
CONTEXTE MÉTIER DYNAMIQUE :
Aucune question utilisateur fournie.

RAPPEL SCHÉMA COMPACT :
{compact}
"""

    relevant = get_relevant_column_descriptions(
        user_question=user_question,
        tables=None,
        max_per_table=5,
    )

    if relevant:
        return f"""
CONTEXTE MÉTIER DYNAMIQUE :
Les colonnes ci-dessous sont les plus pertinentes pour cette question.
Priorise-les. Respecte strictement :
- "✅ UTILISER POUR"
- "❌ NE PAS UTILISER POUR"
- "📊 Agrégation"
- "⚠️ PIÈGE"
- "🔗 Jointure"

{relevant}
"""

    compact = get_all_column_descriptions_compact(
        tables=["events_clean", "mentions_clean", "gkg_clean"]
    )
    return f"""
CONTEXTE MÉTIER DYNAMIQUE :
Aucune colonne n'a matché fortement la question.
Utilise ce rappel compact du schéma, sans inventer de colonnes.

{compact}
"""


# ════════════════════════════════════════════════════════════════
# ASSEMBLAGE FINAL
# ════════════════════════════════════════════════════════════════

def get_system_prompt(user_question: str = "") -> str:
    """
    Construit le prompt système complet :
    1. Prompt statique (règles, schéma, exemples)
    2. Patterns SQL pertinents (few-shot dynamique)
    3. Anti-patterns (garde-fous)
    4. Schéma dynamique (colonnes pertinentes)
    5. Règles de raisonnement
    """
    # Blocs dynamiques
    dynamic_schema_block = _build_dynamic_schema_block(user_question)
    query_patterns_block = _build_query_patterns_block(user_question)
    anti_patterns_block = _build_anti_patterns_block()

    # Assemblage
    parts = [_STATIC_PROMPT]

    if query_patterns_block:
        parts.append(f"\n{query_patterns_block}\n")

    if anti_patterns_block:
        parts.append(f"\n{anti_patterns_block}\n")

    parts.append(f"""
RÈGLES DE RAISONNEMENT :
- Priorise les colonnes du CONTEXTE MÉTIER DYNAMIQUE si pertinentes.
- Si une colonne a une note de confusion fréquente, applique-la strictement.
- Si une colonne indique une jointure interdite, ne la fais jamais.
- Préfère les colonnes enrichies lisibles aux colonnes brutes.
- Pour un "top", ajoute ORDER BY ... DESC LIMIT 10 ou LIMIT 20.
- Pour une série temporelle mensuelle, trie par la colonne de mois.
- Pour une seule valeur agrégée → chart_recommendation = "kpi".
- Pour un classement → chart_recommendation = "bar".
- Pour une évolution temporelle → chart_recommendation = "line".
- Pour une analyse géographique → chart_recommendation = "map".
- VÉRIFIE TOUJOURS que chaque alias.colonne pointe vers la bonne table.

{dynamic_schema_block}
""")

    return "\n".join(parts)