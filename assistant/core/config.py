"""
config.py
Configuration centrale du chatbot GDELT Bénin Assistant.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ═══════════════════════════════════════════════════════════════
# BIGQUERY
# ═══════════════════════════════════════════════════════════════

BQ_PROJECT = "gdelt-494812"
BQ_DATASET = "benin_2025"

BQ_TABLES = {
    "events": f"{BQ_PROJECT}.{BQ_DATASET}.events_clean",
    "mentions": f"{BQ_PROJECT}.{BQ_DATASET}.mentions_clean",
    "gkg": f"{BQ_PROJECT}.{BQ_DATASET}.gkg_clean",
}

# ═══════════════════════════════════════════════════════════════
# SÉCURITÉ SQL
# ═══════════════════════════════════════════════════════════════

DEFAULT_LIMIT = None
MAX_ROWS = None
YEAR_FILTER = 2025

FORBIDDEN_SQL_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
    "CREATE", "TRUNCATE", "MERGE", "REPLACE",
    "GRANT", "REVOKE", "EXEC", "EXECUTE", "CALL",
]

# ═══════════════════════════════════════════════════════════════
# CAS D'USAGE AUTORISÉS
# ═══════════════════════════════════════════════════════════════

ALLOWED_INTENTS = [
    # Comptages
    "count_events",
    "count_mentions",
    "count_articles",

    # Classements / top
    "top_sources",
    "top_themes",
    "top_persons",
    "top_organizations",
    "top_locations",

    # Tendances
    "trend_analysis",
    "monthly_trend",
    "tone_trend",

    # Tonalité
    "event_tone_analysis",
    "mention_tone_analysis",
    "article_tone_analysis",

    # Couverture médiatique
    "event_media_coverage",
    "media_coverage_analysis",

    # Géographie
    "geo_analysis",
    "department_analysis",
    "map_analysis",

    # Événements
    "significant_events",
    "international_actors",
    "event_category_analysis",

    # Fallbacks contrôlés
    "clarification_needed",
    "out_of_scope_question",
    "unknown",
]

# ═══════════════════════════════════════════════════════════════
# CAS D'USAGE REFUSÉS
# ═══════════════════════════════════════════════════════════════

FORBIDDEN_INTENTS = [
    "write_data",
    "schema_modification",
    "prediction_request",
    "personal_data_request",
    "cross_dataset_query",
]

# ═══════════════════════════════════════════════════════════════
# COLONNES AUTORISÉES — SCHÉMA RÉEL BIGQUERY
# ═══════════════════════════════════════════════════════════════

ALLOWED_COLUMNS = {
    "events_clean": {
        "GLOBALEVENTID", "DATEADDED", "SQLDATE", "MonthYear", "Year",
        "Actor1Name", "Actor1CountryCode", "Actor1Type1Code",
        "Actor2Name", "Actor2CountryCode", "Actor2Type1Code",
        "IsRootEvent", "EventCode", "EventBaseCode", "EventRootCode",
        "QuadClass", "GoldsteinScale", "NumMentions", "NumSources", "NumArticles",
        "AvgTone", "ActionGeo_FullName", "ActionGeo_CountryCode",
        "ActionGeo_ADM1Code", "ActionGeo_Lat", "ActionGeo_Long",
        "SOURCEURL", "date_clean", "year_month_clean",
        "QuadClass_Label", "interaction_type", "EventCategory",
        "Actor1Role", "Actor2Role", "goldstein_category", "tone_category",
        "has_international_actor", "event_scope", "is_significant",
    },
    "mentions_clean": {
        "GLOBALEVENTID", "MentionTimeDate", "MentionType",
        "MentionSourceName", "Confidence", "MentionDocTone",
        "MentionDocTranslationInfo", "mention_datetime", "mention_date",
        "mention_year_month", "MentionType_Label", "tone_category",
        "confidence_level", "source_language", "is_translated",
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

# ═══════════════════════════════════════════════════════════════
# GLOSSAIRE MÉTIER → SQL
# ═══════════════════════════════════════════════════════════════

BUSINESS_GLOSSARY = {
    # Gravité — events_clean
    "événement grave": "GoldsteinScale <= -5",
    "événements graves": "GoldsteinScale <= -5",
    "événement très grave": "GoldsteinScale <= -7",
    "événements très graves": "GoldsteinScale <= -7",
    "événement critique": "GoldsteinScale <= -9",
    "événements critiques": "GoldsteinScale <= -9",

    # Tonalité / intensité
    "événement positif": "GoldsteinScale >= 3",
    "événements positifs": "GoldsteinScale >= 3",
    "événement neutre": "GoldsteinScale BETWEEN -2 AND 2",
    "événements neutres": "GoldsteinScale BETWEEN -2 AND 2",

    # Significativité
    "événement significatif": "is_significant = TRUE",
    "événements significatifs": "is_significant = TRUE",

    # Acteurs
    "acteurs internationaux": "has_international_actor = TRUE",
    "acteur international": "has_international_actor = TRUE",

    # Couverture
    "couverture médiatique": "COUNT(*)",
    "top médias": "GROUP BY MentionSourceName ORDER BY COUNT(*) DESC",
}

# ═══════════════════════════════════════════════════════════════
# RÈGLES DE JOINTURE ENTRE TABLES
# ═══════════════════════════════════════════════════════════════

JOIN_RULES = {
    "events_mentions": {
        "left_table": "events_clean",
        "right_table": "mentions_clean",
        "on": "events_clean.GLOBALEVENTID = mentions_clean.GLOBALEVENTID",
        "type": "JOIN",
        "description": (
            "Relie chaque événement à ses mentions médiatiques. "
            "Utilisée pour analyser la couverture médiatique, "
            "les médias sources et la tonalité des mentions."
        ),
    },
}

# ═══════════════════════════════════════════════════════════════
# LLM — OLLAMA
# ═══════════════════════════════════════════════════════════════

LLM_PROVIDER    = "groq"
LLM_MODEL       = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = float(os.environ.get("LLM_TEMPERATURE", "0.0"))

# ═══════════════════════════════════════════════════════════════
# VISUALISATIONS
# ═══════════════════════════════════════════════════════════════

CHART_TYPES = {
    "kpi": "Une seule valeur numérique retournée",
    "bar": "Une catégorie et une mesure, utile pour les classements et comparaisons",
    "line": "Une dimension temporelle et une mesure, utile pour les tendances",
    "pie": "Répartition en parts d'un total",
    "map": "Données géographiques avec latitude et longitude",
    "table": "Résultat tabulaire complexe ou fallback universel",
}