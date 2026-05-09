# assistant/core/response_builder.py

from typing import Any, Dict, List, Optional


def build_sql_error_response(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    return {
        "status": "sql_error",
        "user_message": (
            "La requête générée n’a pas passé les règles de sécurité "
            "ou n’a pas pu être exécutée."
        ),
        "message": message,
        "details": details,
        "data": None,
    }


def build_clarification_response(
    message: str,
    options: List[Dict[str, str]],
    clarification_type: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "status": "clarification_required",
        "user_message": "La question est comprise, mais elle doit être précisée.",
        "message": message,
        "clarification_type": clarification_type,
        "options": options,
        "data": None,
    }


def build_empty_result_response(message: Optional[str] = None) -> Dict[str, Any]:
    return {
        "status": "empty_result",
        "user_message": "Je n’ai trouvé aucun résultat pour cette combinaison de filtres.",
        "message": message or "Aucune ligne n’a été retournée par la requête.",
        "data": [],
    }


def build_result_too_large_response(
    row_count: int,
    max_display_rows: int,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "status": "result_too_large",
        "user_message": (
            "La requête a bien fonctionné, mais le résultat est trop volumineux "
            "pour être affiché directement de manière lisible."
        ),
        "message": message or (
            f"La requête retourne {row_count} lignes, au-delà du seuil "
            f"d’affichage ({max_display_rows})."
        ),
        "row_count": row_count,
        "max_display_rows": max_display_rows,
        "data": None,
    }


def build_success_response(
    sql: str,
    rows: List[Dict[str, Any]],
    chart_type: Optional[str] = None,
    title: Optional[str] = None,
    chart_plan: Optional[Dict[str, Any]] = None,
    summary: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Réponse standard de succès.

    - chart_type : 'bar' | 'line' | 'pie' | 'map' | 'kpi' | 'table'
    - chart_plan : dict optionnel avec les détails (x, y, lat, lon, etc.)
    - summary / suggestion : textes optionnels, peuvent être remplis
      plus tard côté back, ou laissés à None pour être calculés côté UI.
    """
    return {
        "status": "success",
        "user_message": "Analyse terminée avec succès.",
        "message": None,
        "sql": sql,
        "chart_type": chart_type,
        "chart_plan": chart_plan,
        "title": title,
        "summary": summary,
        "suggestion": suggestion,
        "data": rows,
    }