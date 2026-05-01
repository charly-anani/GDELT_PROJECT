# COMMENT UTILISER CES FICHIERS — LISEZ EN PREMIER

## Les 3 fichiers que tu viens de recevoir

| Fichier | Ou le mettre | Ce qu'il fait |
|---|---|---|
| `exploration.ipynb` | `notebooks/exploration.ipynb` | Visualisations EDA (8 graphiques) |
| `ml_model.ipynb` | `notebooks/ml_model.ipynb` | Clustering + classifieur + métriques |
| `app.py` | `dashboard/app.py` | Dashboard Streamlit interactif |

---

## ETAPE 1 — Installer les dépendances (une seule fois)

```bash
# Activer l'environnement virtuel
source .venv/bin/activate     # Mac/Linux
.venv\Scripts\activate        # Windows

# Installer
pip install -r requirements.txt
```

Si `google-cloud-bigquery` n'est pas dans ton requirements.txt, ajoute :

```bash
pip install google-cloud-bigquery plotly scikit-learn joblib streamlit
```

---

## ETAPE 2 — S'authentifier à BigQuery (une seule fois)

```bash
gcloud auth application-default login
```

Cela ouvre un navigateur. Tu te connectes avec le compte Google
qui a accès au projet `gdelt-494812`.

---

## ETAPE 3 — Lancer le notebook d'exploration

```bash
jupyter notebook
```

1. Ouvrir `notebooks/exploration.ipynb`
2. Cliquer sur **Kernel > Restart & Run All**
3. Attendre — chaque cellule se lance dans l'ordre
4. **Ce que tu vas voir :**
   - La liste de tes colonnes réelles s'affiche en cellule 3
   - 8 graphiques Plotly interactifs apparaissent directement dans le notebook
   - Un résumé statistique s'affiche à la fin

> Si une visualisation ne s'affiche pas, vérifie la cellule 3 :
> elle te dit exactement quelles colonnes ont été trouvées.
> Si une colonne est marquée "NON TROUVEE", corrige manuellement
> la variable correspondante (ex: COL_TONE = 'nom_reel_dans_ta_table')

---

## ETAPE 4 — Lancer le notebook ML

```bash
# Dans Jupyter, ouvrir notebooks/ml_model.ipynb
# Kernel > Restart & Run All
```

**Ce que tu vas voir :**
- La courbe du coude + score de silhouette pour choisir le nombre de clusters
- Un scatter plot PCA 2D des clusters
- Un rapport de classification (precision, recall, F1 par classe)
- Une matrice de confusion
- Un graphique d'importance des variables
- La comparaison Random Forest vs Gradient Boosting
- Un résumé final avec toutes les métriques à copier dans le rapport

**Adapter le notebook :**
- Cellule "Cluster names" : change les noms selon ce que tu vois dans les profils
- `K_FINAL` : change la valeur si tu veux un k différent du k suggéré automatiquement

**Les modèles sont sauvegardés automatiquement dans `/models/` :**
- `sentiment_classifier.pkl`
- `kmeans_events.pkl`
- `scaler_cluster.pkl`
- `model_metadata.json` (métriques pour le README)

---

## ETAPE 5 — Lancer le dashboard Streamlit

```bash
streamlit run dashboard/app.py
```

Cela ouvre automatiquement `http://localhost:8501` dans ton navigateur.

**Ce que tu vas voir :**
- 5 KPIs en haut (nb événements, ton moyen, Goldstein, type dominant, % positif)
- Sidebar avec filtres temporels, type d'événement, sentiment
- Volume mensuel + camembert des types
- Barres du ton et Goldstein par mois
- Carte interactive des événements géolocalisés
- Top 15 acteurs + heatmap sentiment
- Section thèmes GKG (cliquer sur le bouton pour charger)

---

## ETAPE 6 — Déployer le dashboard en ligne (pour la soumission)

1. S'inscrire sur [share.streamlit.io](https://share.streamlit.io) (gratuit)
2. Connecter le repo GitHub
3. Choisir `dashboard/app.py` comme fichier principal
4. Dans **Settings > Secrets**, coller :

```toml
[gcp_service_account]
type = "service_account"
project_id = "gdelt-494812"
private_key_id = "..."
private_key = "-----BEGIN RSA PRIVATE KEY-----\n..."
client_email = "..."
client_id = "..."
```

   (Le DE crée le service account dans Google Cloud Console)

5. Cliquer **Deploy** — URL publique disponible en ~2 minutes

---

## Si quelque chose ne marche pas

**Erreur "403 Access Denied" BigQuery**
→ Ton compte n'a pas accès au projet. Demande au DE de t'ajouter
  comme "BigQuery Data Viewer" dans la console GCP.

**Graphique vide ou erreur sur une colonne**
→ Aller en cellule 3 du notebook, corriger manuellement le nom de la colonne.
  Ex : `COL_TONE = 'avg_tone'` si ta table l'appelle comme ça.

**Dashboard qui ne se charge pas en ligne**
→ Vérifier les secrets Streamlit, s'assurer que le service account
  a les droits BigQuery sur le projet `gdelt-494812`.
