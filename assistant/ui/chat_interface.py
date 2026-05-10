# assistant/ui/chat_interface.py

import time
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

from assistant.core.nl2sql import process_user_question
from assistant.core.chart_router import build_chart, choose_chart
from assistant.core.explainer import get_explanation

# Exemples de questions avec icônes
EXAMPLE_QUESTIONS = [
    {
        "icon": "📊",
        "text": "Combien d'événements ont été enregistrés au Bénin en 2025 ?",
    },
    {
        "icon": "📰",
        "text": "Quels sont les 10 médias qui couvrent le plus les événements ?",
    },
    {
        "icon": "📈",
        "text": "Quelle est l'évolution mensuelle de la tonalité moyenne des articles ?",
    },
    {
        "icon": "🏷️",
        "text": "Quels sont les thèmes les plus fréquents dans les articles riches à tonalité négative ?",
    },
    {
        "icon": "🗺️",
        "text": "Où se concentrent les événements de coopération au Bénin ?",
    },
    {
        "icon": "🤝",
        "text": "Quels acteurs sont les plus souvent en conflit ?",
    },
]

def init_session_state():
    """Initialise l'état de la session Streamlit."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_example_questions():
    """Affiche les questions d'exemple sous forme de cartes."""
    col1, col2, col3 = st.columns(3)
    
    for idx, q in enumerate(EXAMPLE_QUESTIONS):
        col = [col1, col2, col3][idx % 3]
        with col:
            if st.button(
                f"{q['icon']}\n\n{q['text']}", 
                key=f"example_{idx}",
                use_container_width=True,
                help="Cliquez pour poser cette question"
            ):
                st.session_state.user_input = q['text']
                st.rerun()

def display_chat_history():
    """Affiche l'historique des messages du chat."""
    for message in st.session_state.messages:
        role = message.get("role")
        
        if role == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="user-message-content">{message.get("content", "")}</div>
            </div>
            """, unsafe_allow_html=True)
        elif role == "assistant":
            # Afficher le contenu en fonction du type
            if "dataframe" in message:
                st.markdown("""<div class="assistant-message">""", unsafe_allow_html=True)
                st.dataframe(message["dataframe"], use_container_width=True)
                st.markdown("""</div>""", unsafe_allow_html=True)
            elif "chart" in message:
                st.markdown("""<div class="assistant-message">""", unsafe_allow_html=True)
                if isinstance(message["chart"], go.Figure):
                    st.plotly_chart(message["chart"], use_container_width=True)
                elif isinstance(message["chart"], folium.Map):
                    st_folium(message["chart"], width=None, height=500)
                st.markdown("""</div>""", unsafe_allow_html=True)
            elif "kpi" in message:
                st.markdown("""<div class="assistant-message">""", unsafe_allow_html=True)
                st.metric(label=message["kpi"]["label"], value=message["kpi"]["value"])
                st.markdown("""</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="assistant-message">
                    <div class="assistant-message-content">{message.get("content", "")}</div>
                </div>
                """, unsafe_allow_html=True)

def handle_user_input():
    """Gère la saisie de l'utilisateur et met à jour le chat."""
    prompt = st.chat_input("Posez votre question ici...", key="chat_input")
    
    # Gérer le cas où l'utilisateur clique sur une question d'exemple
    if "user_input" in st.session_state and st.session_state.user_input:
        prompt = st.session_state.user_input
        st.session_state.user_input = "" # Réinitialiser pour éviter la répétition

    if prompt:
        # Ajouter le message de l'utilisateur à l'historique
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Afficher le message utilisateur immédiatement
        st.markdown(f"""
        <div class="user-message">
            <div class="user-message-content">{prompt}</div>
        </div>
        """, unsafe_allow_html=True)

        # Afficher une réponse de l'assistant en cours de traitement
        with st.spinner("Analyse en cours..."):
            t0 = time.time()
            response = process_user_question(prompt)
            elapsed = time.time() - t0

        # Construire la réponse de l'assistant
        assistant_response_content = f"**{response.get('title', 'Analyse terminée')}**"
        
        # Afficher les données ou le graphique
        df = pd.DataFrame(response.get("data", []))
        chart_type = response.get("chart_type")

        st.markdown("""<div class="assistant-message">""", unsafe_allow_html=True)
        st.markdown(assistant_response_content)

        if not df.empty:
            if chart_type == "kpi" and df.shape == (1, 1):
                label = df.columns[0]
                value = df.iloc[0, 0]
                st.metric(label=label, value=f"{value:,}".replace(",", " "))
                st.session_state.messages.append({"role": "assistant", "kpi": {"label": label, "value": value}})
            else:
                # Obtenir le plan de graphique avec les colonnes détectées
                chart_plan = choose_chart(df, prompt)
                chart = build_chart(df, chart_plan)
                if chart:
                    if isinstance(chart, go.Figure):
                        st.plotly_chart(chart, use_container_width=True)
                    elif isinstance(chart, folium.Map):
                        st_folium(chart, width=None, height=500)
                    st.session_state.messages.append({"role": "assistant", "chart": chart})
                else:
                    st.dataframe(df, use_container_width=True)
                    st.session_state.messages.append({"role": "assistant", "dataframe": df})
        
        # Ajouter l'explication et les détails techniques
        with st.expander("Voir les détails de l'analyse"):
            explanation = get_explanation(prompt, response.get('sql', ''), response.get('explanation_hint', ''))
            st.markdown(explanation)
            st.code(response.get('sql', 'Pas de SQL généré.'), language='sql')
            st.caption(f"Temps de réponse : {elapsed:.2f} secondes.")
        
        st.markdown("""</div>""", unsafe_allow_html=True)

        # Ajouter la réponse complète de l'assistant à l'historique (pour l'affichage simple)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
        
        # Forcer le rechargement pour afficher le nouveau message
        st.rerun()




def _render_table(df: pd.DataFrame) -> None:
    st.dataframe(df, use_container_width=True)


def _render_plotly_or_map(df: pd.DataFrame, response: Dict[str, Any]) -> bool:
    # Obtenir le plan de graphique avec les colonnes détectées
    question = response.get("user_message", "")
    chart_plan = choose_chart(df, question)

    obj = build_chart(df, chart_plan)

    if obj is None:
        return False

    chart_type = chart_plan.get("chart_type")

    if chart_type == "map":
        if HAS_STREAMLIT_FOLIUM:
            st_folium(obj, width=None, height=650)
        else:
            st.components.v1.html(obj._repr_html_(), height=650, scrolling=False)
        return True

    st.plotly_chart(obj, use_container_width=True)
    return True


def render_result(response: Dict[str, Any]) -> None:
    status = response.get("status", "success")

    if status != "success":
        st.error(response.get("user_message", "Une erreur est survenue."))
        if response.get("sql"):
            with st.expander("SQL générée"):
                st.code(response["sql"], language="sql")
        return

    user_message = response.get("user_message")
    if user_message:
        st.success(user_message)

    title = response.get("title")
    if title:
        st.subheader(title)

    df = _to_dataframe(response)
    chart_type = response.get("chart_type", "table")

    if response.get("sql"):
        with st.expander("SQL générée"):
            st.code(response["sql"], language="sql")

    if df.empty:
        st.warning("La requête a réussi, mais aucune ligne n’a été retournée.")
        st.info("Essaie une autre période, une autre source ou un autre niveau d’agrégation.")
        return

    if chart_type == "kpi":
        _render_kpi(df, response)
    elif chart_type == "table":
        _render_table(df)
    else:
        rendered = _render_plotly_or_map(df, response)
        if not rendered:
            _render_table(df)
            chart_type = "table"

    summary = response.get("summary") or build_text_summary(df, chart_type)
    if summary:
        st.info(summary)

    suggestion = response.get("suggestion") or suggest_alternative_view(df, chart_type)
    if suggestion:
        st.caption(suggestion)


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")

        with st.chat_message(role):
            if isinstance(content, str) and content.strip():
                st.markdown(content)

            response = msg.get("response")
            if isinstance(response, dict):
                render_result(response)