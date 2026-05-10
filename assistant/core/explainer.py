# assistant/core/explainer.py

from assistant.core.llm_client import llm_chat
import json


def get_explanation(user_question: str, sql: str, explanation_hint: str) -> str:
    """
    Génère une explication simple de la requête SQL exécutée.
    """
    try:
        if explanation_hint:
            return f"Pour répondre à votre question, j'ai analysé : {explanation_hint}"
        return "Une analyse des données a été effectuée pour répondre à votre question."
    except Exception as e:
        print(f"Erreur lors de la génération de l'explication : {e}")
        return "Une analyse des données a été effectuée pour répondre à votre question."


def get_data_insights(user_question: str, data: list, sql: str = "") -> str:
    """
    Génère une interprétation stricte et factuellement basée sur les résultats.
    
    Analyse les données réelles et produit un insight clé en 2-3 phrases MAX.
    Ne doit JAMAIS inventer ou supposer des valeurs/noms qui ne sont pas dans les données.
    """
    if not data:
        return "Aucune donnée trouvée pour cette requête."
    
    try:
        # Créer un résumé des données réelles - PAS D'INVENTION
        if len(data) == 1:
            # KPI: une seule valeur
            row = data[0]
            key = list(row.keys())[0]
            value = row[key]
            
            if isinstance(value, (int, float)):
                data_summary = f"Résultat unique: {key} = {value:,.0f}"
            else:
                data_summary = f"Résultat: {key} = {value}"
        else:
            # Tableau: passer les vraies données (limite à 15 lignes pour pas surcharger)
            import json
            data_to_show = data[:15]  # Max 15 lignes
            
            # Formater les données de manière lisible
            data_str = "Données:\n"
            for i, row in enumerate(data_to_show, 1):
                data_str += f"{i}. {', '.join([f'{k}: {v}' for k, v in row.items()])}\n"
            
            data_summary = data_str
            if len(data) > 15:
                data_summary += f"\n... et {len(data) - 15} autres lignes"
        
        # Prompt amélioré: analyse approfondie avec contexte
        system_prompt = """Tu es un analyste de données GDELT Bénin expert en géopolitique ouest-africaine.

RÈGLES STRICTES:
1. Analyse UNIQUEMENT les données fournies - ne suppose RIEN
2. Utilise EXACTEMENT les noms/valeurs présents dans les données
3. APPROFONDIR: explique POURQUOI ces résultats, qu'est-ce que ça signifie pour la réalité
4. Ajoute du CONTEXTE: comment cela reflète les enjeux actuels au Bénin/région
5. Relie aux RÉALITÉS: politique, sécurité, médias régionaux (ex: % médias nigérians vs locaux)
6. Parle en français clair et analytique (3-4 phrases max)
7. INTERDIT: inventer des valeurs, supposer des résultats non dans les données

CONTEXTE UTILE (si pertinent):
- Bénin: petit pays ouest-africain, bordé par Togo/Burkina/Niger
- Couverture médiatique souvent dominée par médias nigérians/panafricains
- GDELT suit événements: conflits, gouvernance, mouvements sociaux, etc."""
        
        user_prompt = f"""Question: {user_question}

{data_summary}

Donne une analyse approfondie (3-4 phrases):
1. QUE montrent les données (résultat principal)
2. POURQUOI ce pattern (contexte régional/local)
3. QU'EST-CE que cela signifie pour la réalité du Bénin maintenant:"""
        
        insight = llm_chat(system_prompt, user_prompt)
        return insight.strip()
        
    except Exception as e:
        print(f"Erreur lors de la génération d'insight : {e}")
        return f"Analyse effectuée. {len(data)} résultat(s) obtenu(s)."
