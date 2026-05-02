# GDELT Project

Analyse des événements médiatisés au Bénin via GDELT v2.0 dans Google BigQuery.

**Statut** : Work in Progress. Architecture et flux en place ; documentation et contenu détaillé à suivre.

---

## À propos du projet

- **Données** : GDELT Event Database v2.0 (mise à jour tous les 15 minutes)
- **Couverture** : 12 derniers mois, focus Bénin
- **Source unique de vérité** : Google BigQuery (pas de pipeline local d'extraction)
- **Référence** : GDELT Event Database Data Format Codebook v2.0 (février 2015)

---

## Contexte BigQuery

- **Projet BigQuery** : `gdelt-494812`
- **Dataset** : `benin_2025`
- **Tables** : `events_clean`, `mentions_clean`, `gkg_clean`
- Documentation BigQuery : [config/bigquery.md](config/bigquery.md)
- Dictionnaire de données : [data/data_dictionary.md](data/data_dictionary.md)

---

## Architecture

```text
GDELT Project/
├── README.md
├── requirements.txt
├── config/
│   └── bigquery.md                (connexion et paramètres)
├── dashboard/
│   └── app.py                     (interface visualisation)
├── data/
│   └── data_dictionary.md         (documentation colonnes v2.0)
├── models/                        (à compléter)
├── notebooks/
│   └── exploration.ipynb          (analyse exploratoire)
└── sql/
    ├── 01_extract_events.sql      (requêtes extraction)
    ├── 02_extract_gkg.sql
    ├── 03_extract_mentions.sql
    ├── 04_clean_enrich_events.sql (transformations BigQuery)
    ├── 05_clean_enrich_mentions.sql
    └── 06_clean_enrich_gkg.sql
```

---

## Flux de traitement

1. **Extraction** (`01_extract_*.sql`) : données brutes depuis BigQuery
2. **Nettoyage & Enrichissement** (`04_clean_enrich_*.sql`) : transformation in-place BigQuery
3. **Exploration** (`notebooks/`) : analyse analytique interactive
4. **Visualisation** (`dashboard/`) : interface utilisateur
5. **Documentation** (`data/data_dictionary.md`) : référence colonnes et taxonomies

---

## Authentification BigQuery

L’accès BigQuery est accordé uniquement aux comptes Google autorisés au préalable.

Pour permettre l’exécution locale du notebook, les accès suivants doivent être attribués sur l’adresse e-mail Google de l’évaluateur :

- Au niveau du **projet** `gdelt-494812` : rôle `Utilisateur de job BigQuery` (`BigQuery Job User`) pour permettre l’exécution des requêtes.  
- Au niveau du **dataset** `benin_2025` : rôle `Lecteur de données BigQuery` (`BigQuery Data Viewer`) pour permettre la lecture des tables. 


Concrètement, pour qu’un évaluateur puisse exécuter le notebook, son compte Google doit obligatoirement faire partie de la liste d’e‑mails autorisés ci‑dessous.

### Liste des e-mails autorisés

- [email 1]
- [email 2]
- [email 3]

### Sur Kaggle

1. **Add-ons → Google Cloud Services** → lier son compte Google
2. Activer **BigQuery**
3. **Run All** — aucune configuration supplémentaire, sous réserve que le compte utilisé fasse partie des e-mails autorisés

### En local (VSCode / Jupyter)

Prérequis : avoir [gcloud CLI](https://cloud.google.com/sdk/docs/install) installé. [web:666]

**Windows** : télécharger et exécuter l’installeur  
[GoogleCloudSDKInstaller.exe](https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe)  
— suivre les étapes de l’installeur, il configure tout automatiquement.

**macOS :**
```bash
brew install --cask google-cloud-sdk
```

**Linux (Debian/Ubuntu) :**
```bash
sudo apt-get install google-cloud-cli
```

Ensuite :

```bash
# 1. Installer les dépendances
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. S'authentifier avec son compte Google (à faire une seule fois)
gcloud auth application-default login

# 3. Exécuter le notebook depuis la racine du projet
jupyter notebook notebooks/exploration.ipynb
```

L’étape `gcloud auth application-default login` ouvre le navigateur pour une connexion Google standard et crée les credentials locaux utilisés automatiquement par les bibliothèques BigQuery. [web:664][web:666][web:673]

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```