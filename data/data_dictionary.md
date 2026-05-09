# Data Dictionary — GDELT v2 Benin

Ce document décrit les tables, colonnes et structures de données du projet GDELT v2 opéré sur BigQuery pour l'analyse du Bénin.

## Contexte

- **Projet BigQuery** : `gdelt-494812`
- **Dataset** : `benin_2025`
- **Base** : GDELT v2
- **Périmètre** : 12 derniers mois
- **Source** : BigQuery uniquement

### Accès aux données

Les données sont accessibles via Google BigQuery.

**Sur Kaggle** : l'authentification est automatique. Le compte Google propriétaire du projet se lie directement via **Add-ons → Google Cloud Services**.

**En local** : l'authentification repose sur un Service Account JSON généré depuis [console.cloud.google.com](https://console.cloud.google.com). Le compte de service provient de projet `gdelt-494812` → **IAM & Admin → Comptes de service** (rôles : `Lecteur de données BigQuery` + `Utilisateur de job BigQuery`). La clé JSON est obtenue via **Clés → Créer → JSON**. Le fichier est placé à la racine sous `gdelt-494812-54aad2c4e931.json` (exclu git).

## Tables

La base contient trois tables principales :

### Table `events`

Chaque ligne représente un événement : une action effectuée par un acteur envers un autre acteur à une date et un lieu donnés.

Exemples :

| Colonne | Type | Description | Utilisation |
|---------|------|-------------|-------------|
| **GLOBALEVENTID** | Integer | Identifiant unique assigné à chaque événement (ex: 1234567890) | Clé pour relier aux tables eventmentions et gkg. NB: NON séquentiel par date |
| **Day** | Integer | Date de l'événement au format YYYYMMDD | Colonne de tri principal pour les timelines |
| **DATEADDED** | Integer | Date d'ajout en base au format YYYYMMDDHHMMSS (UTC) | Accès à la résolution 15 minutes |
| **MonthYear** | Integer | Date au format YYYYMM pour agrégation rapide | Analyses mensuelles pré-calculées sans calcul |
| **Year** | Integer | Année au format YYYY | Filtre obligatoire en premier pour économiser quota |
| **Actor1Name** | String | Nom de l'acteur 1 : leader politique, pays, ville, groupe ethnique ou ONG (ex: PATRICE TALON, FRANCE) | Identification principale |
| **Actor1CountryCode** | String | Code CAMEO 3 lettres du pays de l'acteur 1 (BEN, FRA) | Affiliation géographique; peut être blank |
| **Actor2Name** | String | Nom de l'acteur 2 (celui qui subit/reçoit l'action) | Peut être blank en situations single-acteur |
| **Actor2CountryCode** | String | Code CAMEO 3 lettres du pays de l'acteur 2 | Peut être blank si non-identifiable |
| **Actor1Type1Code** | String | Code CAMEO du rôle d'acteur 1 : gouvernement, militaire, police, opposition, rebelles, ONG, médias, réfugiés, etc. | Classification du rôle primaire |
| **Actor2Type1Code** | String | Code CAMEO du rôle d'acteur 2 | Classification du rôle primaire |
| **IsRootEvent** | Integer | 1 = événement en début d'article (proxy d'importance), 0 sinon | LEGACY; SentenceID dans eventmentions pour plus de précision |
| **EventCode** | String | Code CAMEO détaillé décrivant l'action (ex: 0251 = "Appeal for easing of administrative sanctions") | STOCKER EN STRING pour éviter problèmes codes zero-leadés |
| **EventBaseCode** | String | Niveau 2 de la taxonomie CAMEO (ex: 025 = "Appeal to yield"); égal à EventCode pour niveaux 1-2 | STOCKER EN STRING |
| **EventRootCode** | String | Niveau 1 de la taxonomie CAMEO (ex: 02 = "Appeal"); égal à EventCode pour niveaux 1-2 | STOCKER EN STRING; utilisé pour regroupements |
| **QuadClass** | Integer | 4 classifications primaires : 1=Verbal Cooperation, 2=Material Cooperation, 3=Verbal Conflict, 4=Material Conflict | Catégorisation simple pour regroupement haut niveau |
| **GoldsteinScale** | Float | Score de -10 à +10 mesurant impact théorique sur stabilité du pays | Basé sur type d'événement uniquement; peut être agrégé temporellement |
| **NumMentions** | Integer | Total mentions dans mise à jour 15 min (LEGACY) | Composite : mentions brutes + retraitées; utiliser eventmentions |
| **NumSources** | Integer | Nombre de sources distinctes dans mise à jour 15 min (LEGACY) | Recommandé de normaliser; voir eventmentions |
| **NumArticles** | Integer | Nombre d'articles distincts dans mise à jour 15 min (LEGACY) | Voir eventmentions pour analyse détaillée |
| **AvgTone** | Float | Ton moyen (-100=très négatif à +100=très positif, pratiquement -10 à +10) | LEGACY; voir MentionDocTone pour analyse par source |
| **ActionGeo_FullName** | String | Nom complet du lieu où l'action s'est déroulée (ex: "Cotonou, Littoral, Benin") | Contexte géographique; peut contenir variations orthographe |
| **ActionGeo_CountryCode** | String | Code FIPS 2 lettres du pays où l'action s'est déroulée (BN=Bénin) | Filtre principal; plus fiable en zones conflit que Actor_CountryCode |
| **ActionGeo_ADM1Code** | String | Code FIPS du pays + division administrative 1 (État, région, etc.) | Identification fine de région; peut être blank |
| **ActionGeo_Lat** | Float | Latitude du centroïde du lieu pour cartographie | Coordonnées GPS |
| **ActionGeo_Long** | Float | Longitude du centroïde du lieu pour cartographie | Coordonnées GPS |
| **SOURCEURL** | String | URL ou citation du premier article mentionnant cet événement | Traçabilité et vérification |

---

### Table `eventmentions`

Chaque mention d'un événement dans un article reçoit sa propre ligne. Un événement mentionné dans 100 articles = 100 lignes ici.

| Colonne | Type | Description | Utilisation |
|---------|------|-------------|-------------|
| **GLOBALEVENTID** | Integer | ID de l'événement mentionné | Clé pour joindre à `events` |
| **MentionTimeDate** | Integer | Timestamp 15 min (YYYYMMDDHHMMSS) de la mise à jour courant | Identique pour tous les mentions du fichier update |
| **MentionType** | Integer | Type de source : 1=WEB, 2=CITATIONONLY, 3=CORE, 4=DTIC, 5=JSTOR, 6=NONTEXTUALSOURCE | Indique comment accéder au document |
| **MentionSourceName** | String | Identifiant convivial : domaine web, "BBC Monitoring", "JSTOR" | Pour analyse réseau |
| **Confidence** | Integer | % confiance (10-100%) dans l'extraction de cet événement (YYYYMMDDHHMMSS) | Trier pour articles sans ambiguïté |
| **MentionDocTone** | Float | Ton de cet article spécifique (-100 à +100, pratiquement -10 à +10) | Sentiment par source (pas moyenne) |
| **MentionDocTranslationInfo** | String | Infos traduction machine : "srclc:xxx; eng:yyy" si traduit | Langue d'origine et système utilisé |

---

## Table `gkg`

**Note** : Cette table n'est PAS documentée dans le GDELT Event Database Codebook v2.0 officiel (février 2015). Les informations ci-dessous sont complémentaires.

Chaque ligne = un article de presse analysé en profondeur pour thèmes, entités, sentiment.

| Colonne | Type | Description | Utilisation |
|---------|------|-------------|-------------|
| **GKGRECORDID** | String | Identifiant unique de cet enregistrement | Déduplication |
| **DATE** | Timestamp | Date et heure (YYYYMMDDHHMMSS) de publication | Filtrage temporel |
| **SourceCommonName** | String | Nom du média source (ex: bbc.co.uk, lemonde.fr) | Analyser couverture par source |
| **DocumentIdentifier** | String | URL de l'article analysé | Traçabilité |
| **V2Themes** | String | Thèmes détectés, séparés par ; (ex: TERROR;ECON_TRADE;ENV) | Analyse thématique |
| **V2Locations** | String | Lieux mentionnés avec coordonnées | Confirmer localisation |
| **V2Persons** | String | Personnes mentionnées | Graphe d'acteurs |
| **V2Organizations** | String | Organisations mentionnées | Acteurs institutionnels |
| **V2Tone** | String | Sentiment : ton global, scores positif/négatif, polarité, activité | Analyse sentiment détaillée |
| **TranslationInfo** | String | Langue d'origine si traduit | Biais linguistique |
| **SharingImage** | String | URL image principale de l'article | Contenu multimédia |

---

## Relations entre Tables

```
events (1) ──── (N) eventmentions
  │
  └──── (N) gkg (via GLOBALEVENTID)
```

---

## Conformité et Source

Ce dictionnaire de données est basé sur le **GDELT Event Database Data Format Codebook v2.0** (février 2015).

**Colonnes documentées officiellement** : `events` et `eventmentions`  
**Colonne complémentaire** : `gkg` (non incluse dans le Codebook v2.0)

**Version GDELT** : v2.0 avec mise à jour toutes les 15 minutes  
**Codes utilisés** : CAMEO v1.1b3, FIPS pour géolocalisation

**Important** : Les colonnes legacy (`NumMentions`, `NumSources`, `NumArticles`) dans `events` sont incluses pour compatibilité. Utiliser `eventmentions` pour analyse précise de couverture.

