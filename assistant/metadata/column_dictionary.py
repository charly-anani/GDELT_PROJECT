# assistant/metadata/column_dictionary.py

EVENTS_CLEAN_METADATA = {

    # ============================================================
    # IDENTIFIANTS ET DATES — GDELT NATIF
    # ============================================================

    "GLOBALEVENTID": {
        "business_name": "Identifiant unique d'événement",
        "origin": "gdelt_native",
        "definition": "Identifiant numérique unique attribué par GDELT à chaque événement. Chaque ligne de events_clean représente un événement unique identifié par cet ID.",
        "use_for": [
            "compter les événements distincts",
            "joindre events_clean avec mentions_clean",
            "agréger la couverture médiatique par événement",
            "retrouver un événement précis"
        ],
        "avoid_for": [
            "filtrer par plage numérique métier",
            "calculer une moyenne ou une somme",
            "mesure de tonalité ou de gravité"
        ],
        "data_type": "identifiant entier",
        "example_values": ["1082895024", "1082895025"],
        "synonyms": ["événement", "id événement", "event id", "identifiant"],
        "aggregation_hint": "Utiliser dans GROUP BY pour une analyse au niveau événement individuel. COUNT(DISTINCT GLOBALEVENTID) pour compter des événements.",
        "filters_hint": "Ne pas filtrer par plage numérique. Utiliser les colonnes de date pour filtrer dans le temps.",
        "join_role": "Clé de jointure principale avec mentions_clean.GLOBALEVENTID. C'est la SEULE clé de jointure entre events_clean et mentions_clean.",
        "notes": "NE JAMAIS joindre GLOBALEVENTID à une colonne de date comme MentionTimeDate. Ne pas joindre avec gkg_clean, il n'existe pas de clé fiable."
    },

    "DATEADDED": {
        "business_name": "Date d'ingestion GDELT (entier brut)",
        "origin": "gdelt_native",
        "definition": "Date à laquelle l'événement a été ingéré dans GDELT, au format entier YYYYMMDDHHMMSS. C'est une date technique d'ingestion, pas la date de l'événement.",
        "use_for": [
            "analyses techniques ou de latence d'ingestion",
            "vérifications de pipeline"
        ],
        "avoid_for": [
            "analyse temporelle métier",
            "filtrage chronologique des événements"
        ],
        "data_type": "entier brut datetime",
        "example_values": ["20250115120000"],
        "synonyms": [],
        "aggregation_hint": "Préférer date_clean ou year_month_clean pour toute analyse temporelle.",
        "filters_hint": "Préférer Year, date_clean ou year_month_clean pour filtrer.",
        "join_role": "Aucun.",
        "notes": "Colonne technique. Rarement utile dans les questions analytiques."
    },

    "SQLDATE": {
        "business_name": "Date SQL brute de l'événement",
        "origin": "gdelt_native",
        "definition": "Date de l'événement au format entier YYYYMMDD brut GDELT.",
        "use_for": ["vérifications techniques"],
        "avoid_for": [
            "filtrage temporel métier",
            "agrégations temporelles"
        ],
        "data_type": "entier brut date",
        "example_values": ["20250115"],
        "synonyms": [],
        "aggregation_hint": "Toujours préférer date_clean (DATE) ou year_month_clean (STRING) pour des agrégations temporelles propres.",
        "filters_hint": "Préférer Year = 2025 ou date_clean pour filtrer.",
        "join_role": "Aucun.",
        "notes": "Colonne brute GDELT. Utiliser date_clean ou Year à la place."
    },

    "MonthYear": {
        "business_name": "Mois-Année entier brut",
        "origin": "gdelt_native",
        "definition": "Représentation entière du mois et de l'année au format YYYYMM. Exemple : 202501 pour janvier 2025.",
        "use_for": ["agrégations mensuelles si year_month_clean n'est pas disponible"],
        "avoid_for": ["agrégations lisibles ou triables comme STRING"],
        "data_type": "entier YYYYMM",
        "example_values": ["202501", "202506"],
        "synonyms": ["mois", "par mois", "mensuel"],
        "aggregation_hint": "Préférer year_month_clean (STRING '2025-01') pour des agrégations mensuelles plus lisibles et triables.",
        "filters_hint": "MonthYear = 202501 pour janvier 2025.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. year_month_clean est plus propre pour toute agrégation mensuelle."
    },

    "Year": {
        "business_name": "Année de l'événement",
        "origin": "gdelt_native",
        "definition": "Année de l'événement sous forme d'entier. Dans ce dataset, toutes les valeurs sont 2025.",
        "use_for": [
            "filtrer les événements sur l'année 2025",
            "s'assurer que le périmètre temporel est correct"
        ],
        "avoid_for": ["agrégations mensuelles ou journalières"],
        "data_type": "entier",
        "example_values": ["2025"],
        "synonyms": ["année", "2025", "en 2025"],
        "aggregation_hint": "WHERE Year = 2025 est le filtre temporel standard pour events_clean.",
        "filters_hint": "Toujours appliquer WHERE Year = 2025 sauf si la question porte explicitement sur plusieurs années.",
        "join_role": "Aucun.",
        "notes": "Filtre temporel de base pour events_clean."
    },

    # ============================================================
    # ACTEURS — GDELT NATIF
    # ============================================================

    "Actor1Name": {
        "business_name": "Nom de l'acteur principal",
        "origin": "gdelt_native",
        "definition": "Nom de l'entité (pays, organisation, groupe ou individu) qui initie ou réalise l'action dans l'événement.",
        "use_for": [
            "identifier les acteurs principaux",
            "top acteurs les plus impliqués",
            "analyse des relations entre acteurs"
        ],
        "avoid_for": ["analyse géographique des lieux d'action"],
        "data_type": "texte",
        "example_values": ["BENIN", "FRANCE", "UNITED NATIONS"],
        "synonyms": ["acteur", "entité principale", "auteur", "protagoniste", "acteur 1"],
        "aggregation_hint": "GROUP BY Actor1Name pour un top acteurs. Combiner avec Actor2Name si on veut tous les acteurs.",
        "filters_hint": "WHERE Actor1Name = 'FRANCE' pour filtrer par acteur.",
        "join_role": "Aucun.",
        "notes": "Peut être null. Peut contenir des noms en majuscules. Différent de Actor2Name qui est la cible de l'action."
    },

    "Actor1CountryCode": {
        "business_name": "Code pays de l'acteur principal",
        "origin": "gdelt_native",
        "definition": "Code pays ISO à 3 lettres associé à l'acteur principal.",
        "use_for": [
            "filtrer par pays d'origine de l'acteur principal",
            "analyser les acteurs par nationalité"
        ],
        "avoid_for": ["géographie des lieux d'action"],
        "data_type": "code ISO 3 lettres",
        "example_values": ["BEN", "FRA", "USA"],
        "synonyms": ["pays acteur 1", "nationalité acteur"],
        "aggregation_hint": "GROUP BY Actor1CountryCode pour analyse par pays d'acteur.",
        "filters_hint": "WHERE Actor1CountryCode = 'BEN' pour acteurs béninois.",
        "join_role": "Aucun.",
        "notes": "Différent de ActionGeo_CountryCode qui désigne le lieu où l'événement se déroule."
    },

    "Actor1Type1Code": {
        "business_name": "Type de l'acteur principal",
        "origin": "gdelt_native",
        "definition": "Code CAMEO décrivant le type de l'acteur principal (gouvernement, militaire, ONG, groupe rebelle, etc.).",
        "use_for": [
            "analyser les types d'acteurs impliqués",
            "filtrer par catégorie d'acteur"
        ],
        "avoid_for": ["analyse géographique"],
        "data_type": "code CAMEO",
        "example_values": ["GOV", "MIL", "OPP", "NGO"],
        "synonyms": ["type acteur", "catégorie acteur principal"],
        "aggregation_hint": "GROUP BY Actor1Type1Code pour distribution par type d'acteur.",
        "filters_hint": "WHERE Actor1Type1Code = 'GOV' pour acteurs gouvernementaux.",
        "join_role": "Aucun.",
        "notes": "Préférer Actor1Role (colonne enrichie) qui est plus lisible métier."
    },

    "Actor2Name": {
        "business_name": "Nom de l'acteur secondaire (cible de l'action)",
        "origin": "gdelt_native",
        "definition": "Nom de l'entité qui reçoit ou subit l'action dans l'événement. C'est la cible ou le destinataire.",
        "use_for": [
            "analyser les cibles des actions",
            "identifier les acteurs impliqués en tant que destinataires",
            "top acteurs cibles"
        ],
        "avoid_for": ["analyse géographique des lieux d'action"],
        "data_type": "texte",
        "example_values": ["GOVERNMENT", "POLICE", "CITIZENS"],
        "synonyms": ["acteur 2", "cible", "destinataire", "acteur secondaire"],
        "aggregation_hint": "GROUP BY Actor2Name pour top acteurs cibles. Combiner avec Actor1Name pour voir toutes les parties.",
        "filters_hint": "WHERE Actor2Name = 'CITIZENS' pour filtrer les actions ciblant les citoyens.",
        "join_role": "Aucun.",
        "notes": "Peut être null. Différent de Actor1Name qui initie l'action."
    },

    "Actor2CountryCode": {
        "business_name": "Code pays de l'acteur secondaire",
        "origin": "gdelt_native",
        "definition": "Code pays ISO à 3 lettres de l'acteur secondaire.",
        "use_for": ["analyser les cibles par nationalité"],
        "avoid_for": ["géographie du lieu d'action"],
        "data_type": "code ISO 3 lettres",
        "example_values": ["BEN", "NGA", "CHN"],
        "synonyms": ["pays acteur 2"],
        "aggregation_hint": "GROUP BY Actor2CountryCode.",
        "filters_hint": "WHERE Actor2CountryCode = 'BEN'.",
        "join_role": "Aucun.",
        "notes": "Différent de ActionGeo_CountryCode."
    },

    "Actor2Type1Code": {
        "business_name": "Type de l'acteur secondaire",
        "origin": "gdelt_native",
        "definition": "Code CAMEO du type de l'acteur secondaire.",
        "use_for": ["analyser les types de cibles"],
        "avoid_for": ["analyse géographique"],
        "data_type": "code CAMEO",
        "example_values": ["GOV", "CVL", "MIL"],
        "synonyms": ["type acteur 2", "catégorie cible"],
        "aggregation_hint": "GROUP BY Actor2Type1Code.",
        "filters_hint": "WHERE Actor2Type1Code = 'CVL' pour civil.",
        "join_role": "Aucun.",
        "notes": "Préférer Actor2Role (colonne enrichie) pour les questions métier."
    },

    "IsRootEvent": {
        "business_name": "Événement racine",
        "origin": "gdelt_native",
        "definition": "Indicateur binaire (1 ou 0) précisant si cet événement est l'événement principal d'un article ou un événement secondaire dérivé.",
        "use_for": [
            "filtrer uniquement les événements principaux d'un article",
            "éviter le double comptage dans certaines analyses"
        ],
        "avoid_for": ["toute analyse ne nécessitant pas cette granularité"],
        "data_type": "entier booléen (1 ou 0)",
        "example_values": ["1", "0"],
        "synonyms": ["événement principal", "root event"],
        "aggregation_hint": "WHERE IsRootEvent = 1 pour ne garder que les événements racines.",
        "filters_hint": "Filtrer sur IsRootEvent = 1 pour éviter le bruit.",
        "join_role": "Aucun.",
        "notes": "Utile si on veut éviter de compter des événements dupliqués issus d'un même article."
    },

    # ============================================================
    # CODES ÉVÉNEMENTS — GDELT NATIF
    # ============================================================

    "EventCode": {
        "business_name": "Code CAMEO de l'événement",
        "origin": "gdelt_native",
        "definition": "Code CAMEO à 4 chiffres maximum décrivant précisément le type d'action réalisée dans l'événement. C'est le code le plus détaillé de la hiérarchie CAMEO.",
        "use_for": [
            "analyse fine des types d'événements",
            "top événements par code CAMEO"
        ],
        "avoid_for": ["analyse agrégée par grande catégorie"],
        "data_type": "texte code CAMEO",
        "example_values": ["0211", "0251", "1411", "1823"],
        "synonyms": ["code événement", "type précis", "CAMEO code"],
        "aggregation_hint": "GROUP BY EventCode ORDER BY COUNT(*) DESC pour top types précis.",
        "filters_hint": "WHERE EventCode = '14' pour les protestations.",
        "join_role": "Aucun.",
        "notes": "Code le plus granulaire. Préférer EventCategory ou EventBaseCode pour des analyses plus agrégées."
    },

    "EventBaseCode": {
        "business_name": "Code de base de l'événement",
        "origin": "gdelt_native",
        "definition": "Code CAMEO à 2 ou 3 chiffres représentant le type d'événement à un niveau intermédiaire de granularité.",
        "use_for": ["analyse des types d'événements à niveau intermédiaire"],
        "avoid_for": ["analyses très détaillées ou très agrégées"],
        "data_type": "texte code CAMEO",
        "example_values": ["02", "14", "18"],
        "synonyms": ["code base", "code type intermédiaire"],
        "aggregation_hint": "GROUP BY EventBaseCode.",
        "filters_hint": "WHERE EventBaseCode LIKE '14%' pour protestations.",
        "join_role": "Aucun.",
        "notes": "Hiérarchie CAMEO : EventRootCode > EventBaseCode > EventCode."
    },

    "EventRootCode": {
        "business_name": "Catégorie racine de l'événement",
        "origin": "gdelt_native",
        "definition": "Code CAMEO à 2 chiffres représentant la grande famille d'événements : coopération verbale, conflit matériel, etc.",
        "use_for": ["analyse par grande famille d'événements"],
        "avoid_for": ["analyses détaillées"],
        "data_type": "texte code CAMEO",
        "example_values": ["01", "02", "14", "19"],
        "synonyms": ["racine événement", "grande catégorie"],
        "aggregation_hint": "GROUP BY EventRootCode.",
        "filters_hint": "WHERE EventRootCode = '14' pour conflits.",
        "join_role": "Aucun.",
        "notes": "Niveau le plus agrégé de la hiérarchie CAMEO. Pour du métier, préférer EventCategory (enrichi)."
    },

    "QuadClass": {
        "business_name": "Classe quadrant de l'événement (entier)",
        "origin": "gdelt_native",
        "definition": "Classification de l'événement en 4 grandes classes : 1 = Coopération verbale, 2 = Coopération matérielle, 3 = Conflit verbal, 4 = Conflit matériel.",
        "use_for": ["classification rapide coopération/conflit"],
        "avoid_for": ["affichage direct à l'utilisateur"],
        "data_type": "entier (1-4)",
        "example_values": ["1", "2", "3", "4"],
        "synonyms": ["quadrant", "classe événement"],
        "aggregation_hint": "Préférer QuadClass_Label (enrichi) pour l'affichage.",
        "filters_hint": "WHERE QuadClass = 4 pour conflits matériels.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. Pour l'affichage et les analyses, utiliser QuadClass_Label."
    },

    # ============================================================
    # MÉTRIQUES NUMÉRIQUES — GDELT NATIF
    # ============================================================

    "GoldsteinScale": {
        "business_name": "Score de Goldstein (gravité de l'événement)",
        "origin": "gdelt_native",
        "definition": "Score entre -10 et +10 mesurant l'impact théorique de l'événement sur la stabilité du pays. Valeurs négatives = déstabilisant, positives = stabilisant.",
        "use_for": [
            "mesurer la gravité ou l'impact d'un événement",
            "analyser la stabilité géopolitique",
            "trier les événements du plus grave au plus stable"
        ],
        "avoid_for": [
            "mesure de la tonalité médiatique",
            "comptage de volume"
        ],
        "data_type": "float [-10, +10]",
        "example_values": ["-10.0", "-3.5", "0.0", "+4.0", "+7.0"],
        "synonyms": ["gravité", "impact", "stabilité", "score goldstein", "dangerosité"],
        "aggregation_hint": "AVG(GoldsteinScale) pour la gravité moyenne. MIN(GoldsteinScale) pour les événements les plus graves.",
        "filters_hint": "WHERE GoldsteinScale < 0 pour événements déstabilisants.",
        "join_role": "Aucun.",
        "notes": "NE PAS confondre avec AvgTone qui mesure la tonalité médiatique. GoldsteinScale mesure l'impact géopolitique théorique."
    },

    "NumMentions": {
        "business_name": "Nombre de mentions au moment de la détection",
        "origin": "gdelt_native",
        "definition": "Nombre de fois que l'événement a été mentionné dans les articles traités lors de l'ingestion initiale dans GDELT.",
        "use_for": [
            "estimation rapide de l'importance d'un événement sans jointure",
            "proxy de couverture médiatique"
        ],
        "avoid_for": [
            "analyse précise de la couverture médiatique réelle",
            "analyses nécessitant une granularité par source"
        ],
        "data_type": "entier",
        "example_values": ["1", "5", "20"],
        "synonyms": ["mentions", "nombre de mentions"],
        "aggregation_hint": "SUM(NumMentions) pour le total sur un groupe. Pour une analyse précise, préférer la table mentions_clean.",
        "filters_hint": "WHERE NumMentions > 5 pour événements avec couverture minimale.",
        "join_role": "Aucun.",
        "notes": "Colonne agrégée issue de l'ingestion GDELT. Pour une analyse fine de la couverture médiatique, utiliser mentions_clean via GLOBALEVENTID."
    },

    "NumSources": {
        "business_name": "Nombre de sources uniques",
        "origin": "gdelt_native",
        "definition": "Nombre de sources distinctes qui ont couvert l'événement lors de l'ingestion initiale.",
        "use_for": ["estimation rapide de la diversité des sources"],
        "avoid_for": ["analyse détaillée des sources médiatiques"],
        "data_type": "entier",
        "example_values": ["1", "3", "10"],
        "synonyms": ["sources", "diversité médiatique"],
        "aggregation_hint": "AVG(NumSources) ou SUM(NumSources). Pour une analyse précise des sources, utiliser mentions_clean.",
        "filters_hint": "WHERE NumSources > 2 pour événements couverts par plusieurs sources.",
        "join_role": "Aucun.",
        "notes": "Agrégé lors de l'ingestion. Moins précis que l'analyse directe via mentions_clean."
    },

    "NumArticles": {
        "business_name": "Nombre d'articles couvrant l'événement",
        "origin": "gdelt_native",
        "definition": "Nombre d'articles distincts ayant couvert l'événement lors de l'ingestion initiale.",
        "use_for": ["proxy rapide de l'attention médiatique"],
        "avoid_for": ["analyse détaillée de la couverture médiatique"],
        "data_type": "entier",
        "example_values": ["1", "4", "12"],
        "synonyms": ["articles", "nombre d'articles"],
        "aggregation_hint": "SUM(NumArticles) ou AVG(NumArticles).",
        "filters_hint": "WHERE NumArticles > 3 pour les événements largement couverts.",
        "join_role": "Aucun.",
        "notes": "Agrégé à l'ingestion. Pour une analyse précise des articles, utiliser gkg_clean."
    },

    "AvgTone": {
        "business_name": "Tonalité moyenne des articles couvrant l'événement",
        "origin": "gdelt_native",
        "definition": "Tonalité émotionnelle moyenne des articles ayant couvert l'événement. Valeurs négatives = tonalité négative/pessimiste, valeurs positives = tonalité positive/optimiste. Calculée sur les articles traités lors de l'ingestion.",
        "use_for": [
            "mesurer la tonalité médiatique d'un événement",
            "analyser la perception médiatique",
            "comparer la tonalité entre catégories d'événements"
        ],
        "avoid_for": [
            "mesure de la gravité géopolitique",
            "analyse de la couverture en volume"
        ],
        "data_type": "float",
        "example_values": ["-5.2", "-1.3", "0.1", "+2.8"],
        "synonyms": [
            "tonalité", "ton moyen", "sentiment", "tonalité moyenne",
            "polarité", "perception médiatique"
        ],
        "aggregation_hint": "AVG(AvgTone) pour la tonalité moyenne d'un groupe d'événements.",
        "filters_hint": "WHERE AvgTone < 0 pour événements à tonalité négative.",
        "join_role": "Aucun.",
        "notes": "NE PAS confondre avec GoldsteinScale (gravité géopolitique) ni avec MentionDocTone (tonalité d'une mention précise dans mentions_clean)."
    },

    # ============================================================
    # GÉOGRAPHIE — GDELT NATIF
    # ============================================================

    "ActionGeo_FullName": {
        "business_name": "Nom complet du lieu de l'événement",
        "origin": "gdelt_native",
        "definition": "Nom complet du lieu géographique où l'action de l'événement s'est produite (ville, département, région, pays).",
        "use_for": [
            "analyse géographique des événements",
            "top des zones les plus actives",
            "répartition des événements par lieu"
        ],
        "avoid_for": [
            "cartographie précise nécessitant des coordonnées",
            "filtrage par pays (préférer ActionGeo_CountryCode)"
        ],
        "data_type": "texte",
        "example_values": ["Cotonou, Littoral, Benin", "Parakou, Borgou, Benin"],
        "synonyms": [
            "lieu", "zone", "localisation", "ville", "département",
            "région", "géographie", "emplacement"
        ],
        "aggregation_hint": "GROUP BY ActionGeo_FullName ORDER BY COUNT(*) DESC pour top lieux.",
        "filters_hint": "WHERE ActionGeo_FullName LIKE '%Cotonou%' pour filtrer Cotonou.",
        "join_role": "Aucun.",
        "notes": "Peut contenir des valeurs comme 'Benin' sans précision de ville. Pour les cartes, utiliser en combinaison avec ActionGeo_Lat et ActionGeo_Long."
    },

    "ActionGeo_CountryCode": {
        "business_name": "Code pays du lieu de l'événement",
        "origin": "gdelt_native",
        "definition": "Code pays où l'action a eu lieu. Dans ce dataset, pratiquement toutes les valeurs sont 'BN' (Bénin).",
        "use_for": ["vérification du périmètre pays"],
        "avoid_for": ["analyses géographiques fines"],
        "data_type": "code pays",
        "example_values": ["BN"],
        "synonyms": ["pays événement"],
        "aggregation_hint": "Rarement utile dans ce dataset mono-pays.",
        "filters_hint": "WHERE ActionGeo_CountryCode = 'BN' pour s'assurer du périmètre Bénin.",
        "join_role": "Aucun.",
        "notes": "Ce dataset est déjà filtré sur le Bénin, ce filtre est donc redondant mais défensif."
    },

    "ActionGeo_ADM1Code": {
        "business_name": "Code de subdivision administrative (département)",
        "origin": "gdelt_native",
        "definition": "Code de la subdivision administrative de niveau 1 (équivalent département au Bénin) où l'événement s'est produit.",
        "use_for": [
            "analyse par département",
            "cartographie par subdivision administrative"
        ],
        "avoid_for": ["affichage lisible (préférer ActionGeo_FullName)"],
        "data_type": "code texte",
        "example_values": ["BN01", "BN04"],
        "synonyms": ["département", "subdivision", "ADM1"],
        "aggregation_hint": "GROUP BY ActionGeo_ADM1Code pour analyse par département. Combiner avec ActionGeo_FullName pour l'affichage.",
        "filters_hint": "WHERE ActionGeo_ADM1Code = 'BN01' pour un département spécifique.",
        "join_role": "Aucun.",
        "notes": "Préférer ActionGeo_FullName pour l'affichage lisible."
    },

    "ActionGeo_Lat": {
        "business_name": "Latitude du lieu de l'événement",
        "origin": "gdelt_native",
        "definition": "Latitude géographique (décimale) du lieu où l'événement s'est produit.",
        "use_for": [
            "cartographie et visualisation géographique",
            "calcul de distances",
            "hotspot maps"
        ],
        "avoid_for": ["filtrage ou agrégation analytique"],
        "data_type": "float décimal",
        "example_values": ["6.3703", "9.3470"],
        "synonyms": ["latitude", "coordonnées", "map", "carte"],
        "aggregation_hint": "Utiliser avec ActionGeo_Long pour les cartes. AVG(Lat) pour centroïde.",
        "filters_hint": "Rarement utilisé pour filtrer directement.",
        "join_role": "Aucun.",
        "notes": "Toujours utiliser conjointement avec ActionGeo_Long pour la cartographie."
    },

    "ActionGeo_Long": {
        "business_name": "Longitude du lieu de l'événement",
        "origin": "gdelt_native",
        "definition": "Longitude géographique (décimale) du lieu où l'événement s'est produit.",
        "use_for": [
            "cartographie et visualisation géographique",
            "hotspot maps"
        ],
        "avoid_for": ["filtrage ou agrégation analytique"],
        "data_type": "float décimal",
        "example_values": ["2.4183", "2.6000"],
        "synonyms": ["longitude", "coordonnées", "map", "carte"],
        "aggregation_hint": "Utiliser avec ActionGeo_Lat.",
        "filters_hint": "Rarement utilisé pour filtrer directement.",
        "join_role": "Aucun.",
        "notes": "Toujours utiliser conjointement avec ActionGeo_Lat."
    },

    "SOURCEURL": {
        "business_name": "URL de la source de l'événement",
        "origin": "gdelt_native",
        "definition": "URL de l'article ou de la source web ayant servi à détecter l'événement.",
        "use_for": ["identification de la source d'origine", "déduplication"],
        "avoid_for": ["agrégations analytiques"],
        "data_type": "URL texte",
        "example_values": ["https://example.com/article-1"],
        "synonyms": ["url", "lien", "source url", "article source"],
        "aggregation_hint": "Rarement utile pour les agrégations. COUNT(DISTINCT SOURCEURL) pour compter les sources uniques.",
        "filters_hint": "Peut filtrer par domaine avec LIKE '%bbc.%'.",
        "join_role": "Aucun.",
        "notes": "Colonne de traçabilité. Pour l'analyse des sources médiatiques, préférer mentions_clean.MentionSourceName."
    },

    # ============================================================
    # COLONNES ENRICHIES — CRÉÉES PAR LE PIPELINE DE TRAITEMENT
    # ============================================================

    "date_clean": {
        "business_name": "Date propre de l'événement",
        "origin": "enriched",
        "definition": "Date de l'événement au format DATE SQL propre (YYYY-MM-DD), dérivée de SQLDATE. Cette colonne est la référence temporelle journalière à utiliser.",
        "use_for": [
            "filtrage journalier précis",
            "agrégations temporelles journalières",
            "comparaisons de dates"
        ],
        "avoid_for": ["agrégations mensuelles (préférer year_month_clean)"],
        "data_type": "DATE",
        "example_values": ["2025-01-15", "2025-06-22"],
        "synonyms": ["date", "jour", "date de l'événement"],
        "aggregation_hint": "GROUP BY date_clean pour une analyse journalière.",
        "filters_hint": "WHERE date_clean BETWEEN '2025-01-01' AND '2025-03-31'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Toujours préférer date_clean à SQLDATE ou DATEADDED pour les analyses métier."
    },

    "year_month_clean": {
        "business_name": "Mois-Année lisible de l'événement",
        "origin": "enriched",
        "definition": "Représentation mensuelle de l'événement au format STRING 'YYYY-MM'. Dérivée de SQLDATE. C'est la référence pour toute agrégation mensuelle.",
        "use_for": [
            "agrégations mensuelles",
            "séries temporelles mensuelles",
            "évolution mois par mois"
        ],
        "avoid_for": ["analyses journalières ou annuelles"],
        "data_type": "STRING format YYYY-MM",
        "example_values": ["2025-01", "2025-06", "2025-12"],
        "synonyms": [
            "mois", "mensuel", "par mois", "évolution mensuelle",
            "mois-année", "période mensuelle"
        ],
        "aggregation_hint": "GROUP BY year_month_clean ORDER BY year_month_clean pour une série temporelle mensuelle.",
        "filters_hint": "WHERE year_month_clean LIKE '2025-%' ou WHERE year_month_clean = '2025-01'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer year_month_clean à MonthYear (entier brut) pour toute agrégation mensuelle."
    },

    "QuadClass_Label": {
        "business_name": "Libellé de la classe de l'événement",
        "origin": "enriched",
        "definition": "Version texte lisible de QuadClass. Valeurs : 'Verbal Cooperation', 'Material Cooperation', 'Verbal Conflict', 'Material Conflict'.",
        "use_for": [
            "affichage de la catégorie de l'événement",
            "filtrage par type de classe",
            "analyse coopération vs conflit"
        ],
        "avoid_for": ["jointures ou calculs numériques"],
        "data_type": "texte",
        "example_values": [
            "Verbal Cooperation", "Material Cooperation",
            "Verbal Conflict", "Material Conflict"
        ],
        "synonyms": ["catégorie", "type coopération", "type conflit", "classe"],
        "aggregation_hint": "GROUP BY QuadClass_Label pour répartition des types d'événements.",
        "filters_hint": "WHERE QuadClass_Label = 'Material Conflict'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie lisible. Toujours préférer QuadClass_Label à QuadClass (entier) pour l'affichage et les filtres métier."
    },

    "interaction_type": {
        "business_name": "Type d'interaction entre acteurs",
        "origin": "enriched",
        "definition": "Libellé décrivant la nature de l'interaction entre les deux acteurs (ex : Government-Civilian, Government-Opposition, etc.). Dérivé de Actor1Type1Code et Actor2Type1Code.",
        "use_for": [
            "analyser les types de relations entre acteurs",
            "distinguer interactions gouvernement-opposition, état-civil, etc."
        ],
        "avoid_for": ["analyse des lieux ou de la tonalité"],
        "data_type": "texte",
        "example_values": [
            "GOVERNMENT-CIVILIAN", "GOVERNMENT-OPPOSITION",
            "MILITARY-CIVILIAN", "UNKNOWN"
        ],
        "synonyms": ["relation acteurs", "type interaction", "profil interaction"],
        "aggregation_hint": "GROUP BY interaction_type ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE interaction_type = 'GOVERNMENT-CIVILIAN'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus lisible que la combinaison de Actor1Type1Code et Actor2Type1Code."
    },

    "EventCategory": {
        "business_name": "Catégorie métier de l'événement",
        "origin": "enriched",
        "definition": "Catégorie métier lisible de l'événement, dérivée de EventRootCode et EventCode. Exemples : 'Conflit armé', 'Coopération diplomatique', 'Protestation civile', etc.",
        "use_for": [
            "analyse des types d'événements en langage naturel",
            "répartition des événements par catégorie métier",
            "top catégories d'événements"
        ],
        "avoid_for": ["analyses nécessitant les codes CAMEO bruts"],
        "data_type": "texte",
        "example_values": [
            "Conflit armé", "Coopération diplomatique",
            "Protestation civile", "Aide humanitaire"
        ],
        "synonyms": [
            "catégorie événement", "type événement", "nature événement",
            "catégorie", "types d'événements"
        ],
        "aggregation_hint": "GROUP BY EventCategory ORDER BY COUNT(*) DESC pour top catégories.",
        "filters_hint": "WHERE EventCategory = 'Conflit armé'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer EventCategory à EventCode pour toute question métier sur les 'types d'événements'."
    },

    "Actor1Role": {
        "business_name": "Rôle métier de l'acteur principal",
        "origin": "enriched",
        "definition": "Rôle fonctionnel lisible de l'acteur principal, dérivé de Actor1Type1Code. Exemples : 'Government', 'Military', 'Opposition', 'NGO'.",
        "use_for": [
            "analyser les rôles des acteurs principaux",
            "filtrer par type d'acteur en langage métier"
        ],
        "avoid_for": ["analyse géographique"],
        "data_type": "texte",
        "example_values": ["Government", "Military", "Opposition", "Civilian"],
        "synonyms": ["rôle acteur 1", "profil acteur", "type acteur principal"],
        "aggregation_hint": "GROUP BY Actor1Role ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE Actor1Role = 'Military'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer Actor1Role à Actor1Type1Code pour les questions métier."
    },

    "Actor2Role": {
        "business_name": "Rôle métier de l'acteur secondaire",
        "origin": "enriched",
        "definition": "Rôle fonctionnel lisible de l'acteur secondaire, dérivé de Actor2Type1Code.",
        "use_for": [
            "analyser les rôles des acteurs cibles",
            "filtrer par type de cible en langage métier"
        ],
        "avoid_for": ["analyse géographique"],
        "data_type": "texte",
        "example_values": ["Civilian", "Government", "NGO"],
        "synonyms": ["rôle acteur 2", "rôle cible"],
        "aggregation_hint": "GROUP BY Actor2Role ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE Actor2Role = 'Civilian'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer Actor2Role à Actor2Type1Code."
    },

    "goldstein_category": {
        "business_name": "Catégorie de gravité de l'événement",
        "origin": "enriched",
        "definition": "Catégorie textuelle dérivée de GoldsteinScale. Exemples : 'Très grave', 'Grave', 'Neutre', 'Stabilisant'. Dérivée en segmentant la plage [-10, +10] de GoldsteinScale.",
        "use_for": [
            "analyser la répartition des événements par niveau de gravité",
            "filtrer les événements graves ou stabilisants",
            "affichage métier de la gravité"
        ],
        "avoid_for": ["calculs numériques précis sur la gravité"],
        "data_type": "texte catégorie",
        "example_values": [
            "Très grave", "Grave", "Légèrement négatif",
            "Neutre", "Légèrement positif", "Stabilisant"
        ],
        "synonyms": [
            "gravité", "catégorie gravité", "niveau gravité",
            "dangerosité", "intensité"
        ],
        "aggregation_hint": "GROUP BY goldstein_category ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE goldstein_category IN ('Très grave', 'Grave') pour les plus graves.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus lisible que GoldsteinScale brut pour l'affichage et les filtres métier."
    },

    "tone_category": {
        "business_name": "Catégorie de tonalité de l'événement",
        "origin": "enriched",
        "definition": "Catégorie textuelle de la tonalité médiatique dérivée de AvgTone. Exemples : 'Très négatif', 'Négatif', 'Neutre', 'Positif'. Dérivée en segmentant AvgTone.",
        "use_for": [
            "analyser la répartition des événements par tonalité",
            "filtrer par sentiment médiatique",
            "affichage métier de la tonalité"
        ],
        "avoid_for": ["calculs de moyenne sur la tonalité (préférer AvgTone)"],
        "data_type": "texte catégorie",
        "example_values": ["Très négatif", "Négatif", "Neutre", "Positif"],
        "synonyms": [
            "tonalité", "sentiment", "perception", "ton",
            "catégorie tonalité"
        ],
        "aggregation_hint": "GROUP BY tone_category ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE tone_category = 'Très négatif' pour les événements très négatifs.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer tone_category pour l'affichage. Utiliser AVG(AvgTone) pour des calculs de moyenne numérique."
    },

    "has_international_actor": {
        "business_name": "Présence d'un acteur international",
        "origin": "enriched",
        "definition": "Booléen indiquant si au moins un des acteurs de l'événement est d'origine internationale (non béninois). Dérivé en vérifiant si Actor1CountryCode ou Actor2CountryCode est différent de 'BEN'.",
        "use_for": [
            "filtrer les événements impliquant des acteurs internationaux",
            "analyser la dimension internationale des événements",
            "distinguer événements locaux vs internationaux"
        ],
        "avoid_for": ["analyse de la tonalité ou du volume"],
        "data_type": "BOOLEAN",
        "example_values": ["TRUE", "FALSE"],
        "synonyms": [
            "acteurs internationaux", "international",
            "dimension internationale", "acteur étranger"
        ],
        "aggregation_hint": "WHERE has_international_actor = TRUE pour filtrer les événements internationaux.",
        "filters_hint": "WHERE has_international_actor = TRUE.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Utiliser directement comme filtre booléen."
    },

    "event_scope": {
        "business_name": "Portée géographique de l'événement",
        "origin": "enriched",
        "definition": "Catégorie décrivant la portée de l'événement : 'Local', 'National', 'International'. Dérivée en combinant has_international_actor et ActionGeo_CountryCode.",
        "use_for": [
            "distinguer événements locaux, nationaux et internationaux",
            "analyser la répartition de la portée des événements"
        ],
        "avoid_for": ["mesure de gravité ou de tonalité"],
        "data_type": "texte",
        "example_values": ["Local", "National", "International"],
        "synonyms": ["portée", "dimension", "périmètre géographique", "local", "international"],
        "aggregation_hint": "GROUP BY event_scope ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE event_scope = 'International'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus lisible que has_international_actor seul pour les analyses métier."
    },

    "is_significant": {
        "business_name": "Événement significatif",
        "origin": "enriched",
        "definition": "Booléen indiquant si l'événement est considéré comme significatif selon des critères combinés : fort volume de mentions (NumMentions élevé), fort nombre de sources (NumSources élevé), ou score Goldstein extrême.",
        "use_for": [
            "filtrer les événements les plus importants",
            "analyser uniquement les événements significatifs",
            "réduire le bruit dans les analyses"
        ],
        "avoid_for": ["analyse de volume global incluant tous les événements"],
        "data_type": "BOOLEAN",
        "example_values": ["TRUE", "FALSE"],
        "synonyms": [
            "significatif", "important", "majeur", "notable",
            "événement fort", "événements clés"
        ],
        "aggregation_hint": "WHERE is_significant = TRUE pour cibler les événements importants.",
        "filters_hint": "WHERE is_significant = TRUE.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Le critère exact dépend de ton pipeline d'enrichissement. C'est le filtre à utiliser pour toute question sur les 'événements significatifs', 'importants', 'majeurs' ou 'notables'."
    }
}


GKG_CLEAN_METADATA = {

    # ============================================================
    # IDENTIFIANTS ET DATES — GDELT NATIF
    # ============================================================

    "GKGRECORDID": {
        "business_name": "Identifiant unique d'enregistrement GKG",
        "origin": "gdelt_native",
        "definition": "Identifiant unique attribué par GDELT à chaque enregistrement du Knowledge Graph. Format : date + séquence. Représente un article ou une source unique traité par GDELT.",
        "use_for": [
            "compter les articles distincts",
            "dédupliquer les enregistrements",
            "identifier une source GKG précise"
        ],
        "avoid_for": [
            "calculs numériques",
            "filtrage temporel",
            "analyses agrégées"
        ],
        "data_type": "texte identifiant",
        "example_values": ["20250115123456-1", "20250622094500-3"],
        "synonyms": ["id article", "identifiant article", "record id"],
        "aggregation_hint": "COUNT(DISTINCT GKGRECORDID) pour compter les articles uniques.",
        "filters_hint": "Rarement utilisé pour filtrer directement.",
        "join_role": "Aucun. Pas de clé de jointure avec events_clean ou mentions_clean.",
        "notes": "Identifiant technique. Ne jamais joindre à events_clean ou mentions_clean via cet ID."
    },

    "DATE": {
        "business_name": "Date brute GKG (entier)",
        "origin": "gdelt_native",
        "definition": "Date de publication de l'article au format entier brut YYYYMMDDHHMMSS. C'est la date technique d'ingestion GDELT.",
        "use_for": ["vérifications techniques"],
        "avoid_for": [
            "filtrage temporel métier",
            "agrégations temporelles"
        ],
        "data_type": "entier brut datetime",
        "example_values": ["20250115120000"],
        "synonyms": [],
        "aggregation_hint": "Toujours préférer gkg_date (DATE) ou gkg_year_month (STRING) pour les analyses temporelles.",
        "filters_hint": "Préférer gkg_date ou gkg_year_month.",
        "join_role": "Aucun.",
        "notes": "Colonne brute GDELT. Utiliser gkg_date ou gkg_year_month à la place pour tout usage métier."
    },

    "SourceCommonName": {
        "business_name": "Nom de la source de l'article",
        "origin": "gdelt_native",
        "definition": "Nom lisible ou domaine de la source médiatique ayant publié l'article. Correspond au nom du média ou du site web.",
        "use_for": [
            "identifier les médias qui publient sur le Bénin",
            "top sources d'articles",
            "analyser la diversité des sources GKG",
            "comparer la tonalité par source"
        ],
        "avoid_for": [
            "analyse des types de médias (préférer MentionType dans mentions_clean)",
            "comptage de mentions d'événements"
        ],
        "data_type": "texte",
        "example_values": ["bbc.com", "rfi.fr", "24haubenin.com"],
        "synonyms": [
            "source", "média", "journal", "site web",
            "éditeur", "publication", "source d'article"
        ],
        "aggregation_hint": "GROUP BY SourceCommonName ORDER BY COUNT(*) DESC pour top sources d'articles.",
        "filters_hint": "WHERE SourceCommonName LIKE '%rfi%' pour filtrer par média.",
        "join_role": "Aucun.",
        "notes": "Différent de MentionSourceName dans mentions_clean. SourceCommonName concerne les articles GKG. Pour la couverture événementielle par source, utiliser mentions_clean.MentionSourceName."
    },

    "DocumentIdentifier": {
        "business_name": "URL ou identifiant du document source",
        "origin": "gdelt_native",
        "definition": "URL complète ou identifiant unique de l'article ou du document source traité par GDELT.",
        "use_for": [
            "traçabilité vers l'article original",
            "déduplication des articles"
        ],
        "avoid_for": ["agrégations analytiques"],
        "data_type": "URL texte",
        "example_values": ["https://rfi.fr/afrique/20250115-benin-article"],
        "synonyms": ["url article", "lien article", "document"],
        "aggregation_hint": "COUNT(DISTINCT DocumentIdentifier) pour compter les articles uniques.",
        "filters_hint": "Peut filtrer par domaine avec LIKE '%rfi%'.",
        "join_role": "Aucun.",
        "notes": "Colonne de traçabilité. Pour l'analyse des sources, préférer SourceCommonName."
    },

    # ============================================================
    # CHAMPS MULTI-VALEURS GDELT — GDELT NATIF
    # ============================================================

    "V2Themes": {
        "business_name": "Thèmes détectés dans l'article",
        "origin": "gdelt_native",
        "definition": "Liste de thèmes GDELT détectés dans l'article, séparés par des points-virgules ';'. Chaque thème est un identifiant GDELT GKG comme 'SECURITY_SERVICES', 'ECON_DEVELOPMENT', 'HEALTH', etc. Un article peut contenir plusieurs dizaines de thèmes.",
        "use_for": [
            "analyser les thèmes les plus fréquents dans les articles",
            "filtrer les articles par thème",
            "top thèmes couverts par les médias"
        ],
        "avoid_for": [
            "sélection brute sans UNNEST",
            "comptage direct sans explosion du champ"
        ],
        "data_type": "texte multi-valeurs séparé par ';'",
        "example_values": [
            "SECURITY_SERVICES;ECON_DEVELOPMENT;HEALTH",
            "PROTEST;GOVERNMENT;ELECTIONS"
        ],
        "synonyms": [
            "thèmes", "sujets", "topics", "thématiques",
            "sujets couverts", "thèmes médiatiques"
        ],
        "aggregation_hint": "TOUJOURS utiliser UNNEST(SPLIT(V2Themes, ';')) AS theme + WHERE theme != '' + GROUP BY theme pour extraire les thèmes individuels.",
        "filters_hint": "Ne pas filtrer sur V2Themes brut. Utiliser UNNEST(SPLIT(V2Themes, ';')) AS theme WHERE theme = 'SECURITY_SERVICES'.",
        "join_role": "Aucun.",
        "notes": "JAMAIS sélectionner V2Themes brut pour compter les thèmes. Le champ contient plusieurs valeurs séparées par ';'. Pattern obligatoire : UNNEST(SPLIT(V2Themes, ';')) AS theme WHERE theme != ''."
    },

    "V2Locations": {
        "business_name": "Lieux mentionnés dans l'article",
        "origin": "gdelt_native",
        "definition": "Liste de lieux géographiques détectés dans l'article, séparés par ';'. Format complexe contenant le nom du lieu, le code pays et les coordonnées.",
        "use_for": [
            "analyser les lieux mentionnés dans les articles",
            "identifier les zones géographiques couvertes par les médias"
        ],
        "avoid_for": [
            "géographie fine des événements (préférer ActionGeo_* dans events_clean)",
            "sélection brute sans UNNEST"
        ],
        "data_type": "texte multi-valeurs séparé par ';'",
        "example_values": ["Benin#BN#6.37#2.42;Cotonou#BN#6.36#2.43"],
        "synonyms": [
            "lieux GKG", "localisations articles",
            "zones mentionnées", "géographie articles"
        ],
        "aggregation_hint": "Utiliser UNNEST(SPLIT(V2Locations, ';')) AS location WHERE location != ''.",
        "filters_hint": "Utiliser UNNEST pour filtrer par lieu spécifique.",
        "join_role": "Aucun.",
        "notes": "Format complexe. Préférer ActionGeo_FullName dans events_clean pour une géographie propre des événements."
    },

    "V2Persons": {
        "business_name": "Personnes mentionnées dans l'article",
        "origin": "gdelt_native",
        "definition": "Liste de personnes physiques détectées dans l'article, séparées par ';'. Généralement des noms de personnalités politiques, dirigeants, célébrités.",
        "use_for": [
            "analyser les personnes les plus citées",
            "top personnalités mentionnées dans les médias",
            "filtrer les articles citant une personne précise"
        ],
        "avoid_for": [
            "sélection brute sans UNNEST",
            "comptage direct sans explosion du champ"
        ],
        "data_type": "texte multi-valeurs séparé par ';'",
        "example_values": [
            "patrice talon;ousmane zinsou",
            "macron;zelensky"
        ],
        "synonyms": [
            "personnes", "personnalités", "individus",
            "personnes citées", "noms cités", "personnages"
        ],
        "aggregation_hint": "TOUJOURS utiliser UNNEST(SPLIT(V2Persons, ';')) AS person + WHERE person != '' + GROUP BY person ORDER BY COUNT(*) DESC LIMIT 10 pour le top des personnes.",
        "filters_hint": "WHERE person = 'patrice talon' après UNNEST pour filtrer une personne précise.",
        "join_role": "Aucun.",
        "notes": "JAMAIS sélectionner V2Persons brut pour compter les personnes. Pattern obligatoire : UNNEST(SPLIT(V2Persons, ';')) AS person WHERE person != ''. Les noms sont généralement en minuscules."
    },

    "V2Organizations": {
        "business_name": "Organisations mentionnées dans l'article",
        "origin": "gdelt_native",
        "definition": "Liste d'organisations (entreprises, gouvernements, ONG, institutions) détectées dans l'article, séparées par ';'.",
        "use_for": [
            "analyser les organisations les plus citées",
            "top organisations dans les articles",
            "filtrer les articles citant une organisation précise"
        ],
        "avoid_for": [
            "sélection brute sans UNNEST",
            "comptage direct sans explosion du champ"
        ],
        "data_type": "texte multi-valeurs séparé par ';'",
        "example_values": [
            "union africaine;nations unies;croix rouge",
            "gouvernement du bénin;mtn"
        ],
        "synonyms": [
            "organisations", "institutions", "entreprises",
            "organismes", "organisations citées"
        ],
        "aggregation_hint": "TOUJOURS utiliser UNNEST(SPLIT(V2Organizations, ';')) AS org + WHERE org != '' + GROUP BY org ORDER BY COUNT(*) DESC LIMIT 10.",
        "filters_hint": "WHERE org = 'nations unies' après UNNEST.",
        "join_role": "Aucun.",
        "notes": "JAMAIS sélectionner V2Organizations brut pour compter les organisations. Pattern obligatoire identique à V2Persons et V2Themes."
    },

    "V2Tone": {
        "business_name": "Vecteur de tonalité brut de l'article",
        "origin": "gdelt_native",
        "definition": "Chaîne de caractères brute contenant plusieurs dimensions de tonalité séparées par ','. Format : Tone,Positive,Negative,Polarity,ActivityRef,SelfGroupRef,WordCount.",
        "use_for": ["inspection technique des dimensions de tonalité brutes"],
        "avoid_for": [
            "analyse directe de la tonalité",
            "agrégations"
        ],
        "data_type": "texte brut multi-valeurs séparé par ','",
        "example_values": ["-3.5,1.2,4.7,5.9,10.1,0.0,512"],
        "synonyms": [],
        "aggregation_hint": "Préférer les colonnes enrichies : tone, tone_positive, tone_negative, tone_polarity, tone_activity, word_count.",
        "filters_hint": "Ne jamais filtrer sur V2Tone brut.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. Toujours préférer les colonnes enrichies tone, tone_positive, tone_negative pour les analyses métier."
    },

    "TranslationInfo": {
        "business_name": "Informations de traduction",
        "origin": "gdelt_native",
        "definition": "Informations sur la traduction de l'article si celui-ci a été traduit par GDELT. Contient la langue source et les métadonnées de traduction.",
        "use_for": ["vérifier si un article a été traduit"],
        "avoid_for": ["analyses de contenu ou de tonalité"],
        "data_type": "texte",
        "example_values": ["srclc:fr", "srclc:en"],
        "synonyms": ["traduction", "translation info"],
        "aggregation_hint": "Préférer la colonne enrichie is_translated et source_language.",
        "filters_hint": "Préférer WHERE is_translated = TRUE.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. Utiliser is_translated (BOOLEAN) et source_language (STRING) pour les analyses."
    },

    "SharingImage": {
        "business_name": "Image de partage de l'article",
        "origin": "gdelt_native",
        "definition": "URL de l'image principale associée à l'article, utilisée pour le partage sur les réseaux sociaux.",
        "use_for": ["inspection visuelle technique"],
        "avoid_for": ["toute analyse analytique"],
        "data_type": "URL texte",
        "example_values": ["https://example.com/image.jpg"],
        "synonyms": [],
        "aggregation_hint": "Rarement utile dans les analyses.",
        "filters_hint": "WHERE SharingImage IS NOT NULL pour les articles avec image.",
        "join_role": "Aucun.",
        "notes": "Colonne technique rarement utile pour les analyses GDELT."
    },

    # ============================================================
    # DATES ENRICHIES
    # ============================================================

    "gkg_datetime": {
        "business_name": "Timestamp précis de l'article GKG",
        "origin": "enriched",
        "definition": "Timestamp TIMESTAMP au format YYYY-MM-DD HH:MM:SS dérivé de DATE. C'est la référence temporelle précise à la seconde pour les articles GKG.",
        "use_for": [
            "analyses temporelles précises à l'heure ou à la journée",
            "ordonnancement des articles dans le temps"
        ],
        "avoid_for": ["agrégations mensuelles (préférer gkg_year_month)"],
        "data_type": "TIMESTAMP",
        "example_values": ["2025-01-15 12:00:00", "2025-06-22 09:45:00"],
        "synonyms": ["date heure article", "timestamp article"],
        "aggregation_hint": "EXTRACT(HOUR FROM gkg_datetime) pour analyses horaires.",
        "filters_hint": "WHERE gkg_datetime >= '2025-01-01' AND gkg_datetime < '2025-04-01'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus précise que gkg_date mais moins utile pour les agrégations mensuelles."
    },

    "gkg_date": {
        "business_name": "Date de l'article GKG",
        "origin": "enriched",
        "definition": "Date de publication de l'article au format DATE SQL propre (YYYY-MM-DD), dérivée de DATE brut. Référence temporelle journalière pour les articles GKG.",
        "use_for": [
            "filtrage journalier",
            "agrégations journalières",
            "comparaisons de dates"
        ],
        "avoid_for": ["agrégations mensuelles (préférer gkg_year_month)"],
        "data_type": "DATE",
        "example_values": ["2025-01-15", "2025-06-22"],
        "synonyms": ["date article", "date publication"],
        "aggregation_hint": "GROUP BY gkg_date pour analyses journalières.",
        "filters_hint": "WHERE gkg_date BETWEEN '2025-01-01' AND '2025-03-31'. WHERE EXTRACT(YEAR FROM gkg_date) = 2025.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Toujours préférer gkg_date à DATE (entier brut) pour les filtres temporels."
    },

    "gkg_year_month": {
        "business_name": "Mois-Année de l'article GKG",
        "origin": "enriched",
        "definition": "Représentation mensuelle de la date de l'article au format STRING 'YYYY-MM'. C'est la référence pour toute agrégation mensuelle sur les articles GKG.",
        "use_for": [
            "agrégations mensuelles",
            "séries temporelles mensuelles",
            "évolution mois par mois des articles",
            "filtrage de périmètre sur l'année 2025"
        ],
        "avoid_for": ["analyses journalières"],
        "data_type": "STRING format YYYY-MM",
        "example_values": ["2025-01", "2025-06", "2025-12"],
        "synonyms": [
            "mois", "mensuel", "par mois", "évolution mensuelle",
            "période mensuelle", "mois-année"
        ],
        "aggregation_hint": "GROUP BY gkg_year_month ORDER BY gkg_year_month pour série temporelle mensuelle.",
        "filters_hint": "WHERE gkg_year_month LIKE '2025-%' pour toute l'année 2025. WHERE gkg_year_month = '2025-01' pour janvier.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. C'est LE filtre temporel standard pour gkg_clean, équivalent à Year = 2025 pour events_clean."
    },

    # ============================================================
    # TONALITÉ ENRICHIE — EXTRAITE DE V2Tone
    # ============================================================

    "tone": {
        "business_name": "Tonalité globale de l'article",
        "origin": "enriched",
        "definition": "Score de tonalité globale de l'article extrait de V2Tone. Valeurs négatives = article à tonalité négative/pessimiste, valeurs positives = article positif/optimiste. Calculé comme la différence entre mentions positives et négatives.",
        "use_for": [
            "mesurer la tonalité moyenne des articles",
            "filtrer les articles négatifs ou positifs",
            "analyser le sentiment médiatique global",
            "comparer la tonalité entre sources ou thèmes"
        ],
        "avoid_for": [
            "mesure de la gravité géopolitique (préférer GoldsteinScale dans events_clean)",
            "mesure de la couverture médiatique en volume"
        ],
        "data_type": "float",
        "example_values": ["-5.2", "-1.3", "0.0", "+2.8"],
        "synonyms": [
            "tonalité", "ton article", "sentiment article",
            "tonalité globale", "perception", "positif", "négatif",
            "tonalité moyenne des articles"
        ],
        "aggregation_hint": "AVG(tone) pour la tonalité moyenne. WHERE tone < 0 pour articles négatifs.",
        "filters_hint": "WHERE tone < 0 pour articles à tonalité négative. WHERE tone > 0 pour articles positifs.",
        "join_role": "Aucun.",
        "notes": "NE PAS confondre avec AvgTone (tonalité des événements dans events_clean) ni avec MentionDocTone (tonalité d'une mention dans mentions_clean). tone concerne ici les articles GKG."
    },

    "tone_positive": {
        "business_name": "Score de tonalité positive de l'article",
        "origin": "enriched",
        "definition": "Proportion de mots à connotation positive détectés dans l'article. Extrait de V2Tone.",
        "use_for": [
            "analyser la proportion de contenu positif dans les articles",
            "comparer la positivité entre sources"
        ],
        "avoid_for": ["mesure globale de tonalité (préférer tone)"],
        "data_type": "float",
        "example_values": ["1.2", "3.5", "0.0"],
        "synonyms": ["positif", "optimisme", "score positif", "tonalité positive"],
        "aggregation_hint": "AVG(tone_positive) pour la moyenne. GROUP BY SourceCommonName pour comparer par source.",
        "filters_hint": "WHERE tone_positive > 2 pour articles très positifs.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Utiliser en complément de tone pour une analyse bidimensionnelle positive/négative."
    },

    "tone_negative": {
        "business_name": "Score de tonalité négative de l'article",
        "origin": "enriched",
        "definition": "Proportion de mots à connotation négative détectés dans l'article. Extrait de V2Tone. Toujours positif en valeur absolue.",
        "use_for": [
            "analyser la proportion de contenu négatif",
            "identifier les articles les plus négatifs",
            "comparer la négativité entre sources ou thèmes"
        ],
        "avoid_for": ["mesure globale de tonalité (préférer tone)"],
        "data_type": "float (toujours >= 0)",
        "example_values": ["4.7", "2.1", "0.0"],
        "synonyms": ["négatif", "pessimisme", "score négatif", "tonalité négative"],
        "aggregation_hint": "AVG(tone_negative) pour la moyenne de négativité.",
        "filters_hint": "WHERE tone_negative > 5 pour articles très négatifs.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Valeur toujours positive représentant l'intensité négative. Ne pas confondre avec tone (global, peut être négatif ou positif)."
    },

    "tone_polarity": {
        "business_name": "Polarité de l'article",
        "origin": "enriched",
        "definition": "Mesure de la polarité émotionnelle de l'article, calculée comme la somme des scores positifs et négatifs. Plus la valeur est élevée, plus l'article est émotionnellement chargé (dans un sens ou dans l'autre).",
        "use_for": [
            "identifier les articles très chargés émotionnellement",
            "analyser l'intensité du discours médiatique"
        ],
        "avoid_for": ["mesure de direction (positif vs négatif), préférer tone"],
        "data_type": "float",
        "example_values": ["5.9", "2.3", "0.1"],
        "synonyms": [
            "polarité", "charge émotionnelle", "intensité tonale"
        ],
        "aggregation_hint": "AVG(tone_polarity) ou ORDER BY tone_polarity DESC pour les articles les plus polarisés.",
        "filters_hint": "WHERE tone_polarity > 5 pour articles émotionnellement chargés.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Mesure l'intensité émotionnelle, pas la direction. Utiliser tone pour la direction."
    },

    "tone_activity": {
        "business_name": "Niveau d'activité référentielle de l'article",
        "origin": "enriched",
        "definition": "Mesure le niveau d'activité référentielle dans l'article : fréquence de références à des groupes, des acteurs, des entités externes. Extrait de V2Tone.",
        "use_for": [
            "identifier les articles très référencés ou engagés",
            "analyser le niveau d'activité discursive"
        ],
        "avoid_for": ["mesure de tonalité émotionnelle"],
        "data_type": "float",
        "example_values": ["10.1", "3.4", "0.0"],
        "synonyms": ["activité", "référentiel", "engagement discursif"],
        "aggregation_hint": "AVG(tone_activity) pour la moyenne d'activité.",
        "filters_hint": "WHERE tone_activity > 8 pour les articles très actifs.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie technique. Moins utilisée dans les analyses métier courantes."
    },

    "word_count": {
        "business_name": "Nombre de mots de l'article",
        "origin": "enriched",
        "definition": "Nombre de mots détectés dans l'article. Extrait de V2Tone. Permet d'estimer la longueur et la richesse d'un article.",
        "use_for": [
            "filtrer les articles courts ou longs",
            "analyser la richesse éditoriale",
            "pondérer les analyses par longueur d'article"
        ],
        "avoid_for": ["analyse de tonalité ou de couverture"],
        "data_type": "float (entier en pratique)",
        "example_values": ["120.0", "512.0", "1240.0"],
        "synonyms": ["longueur article", "nombre de mots", "taille article"],
        "aggregation_hint": "AVG(word_count) pour la longueur moyenne. WHERE word_count > 300 pour les articles longs.",
        "filters_hint": "WHERE word_count > 200 pour filtrer les articles consistants.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie extraite de V2Tone. Utilisée dans le calcul de is_rich_article."
    },

    "tone_category": {
        "business_name": "Catégorie de tonalité de l'article",
        "origin": "enriched",
        "definition": "Catégorie textuelle de la tonalité dérivée de tone. Valeurs : 'Très négatif', 'Négatif', 'Neutre', 'Positif', 'Très positif'. Dérivée en segmentant la plage de tone.",
        "use_for": [
            "analyser la répartition des articles par catégorie de tonalité",
            "filtrer les articles à tonalité négative ou positive",
            "affichage lisible de la tonalité"
        ],
        "avoid_for": ["calculs numériques sur la tonalité (préférer tone)"],
        "data_type": "texte catégorie",
        "example_values": [
            "Très négatif", "Négatif", "Neutre",
            "Positif", "Très positif"
        ],
        "synonyms": [
            "catégorie tonalité", "sentiment catégorie",
            "tonalité", "articles négatifs", "articles positifs"
        ],
        "aggregation_hint": "GROUP BY tone_category ORDER BY COUNT(*) DESC pour répartition.",
        "filters_hint": "WHERE tone_category = 'Très négatif' ou WHERE tone_category IN ('Négatif', 'Très négatif').",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer tone_category pour l'affichage et les filtres métier. Utiliser AVG(tone) pour les calculs numériques."
    },

    # ============================================================
    # MÉTADONNÉES ENRICHIES
    # ============================================================

    "source_language": {
        "business_name": "Langue de la source de l'article",
        "origin": "enriched",
        "definition": "Code de la langue de l'article source avant traduction éventuelle. Dérivé de TranslationInfo.",
        "use_for": [
            "analyser la diversité linguistique des sources",
            "filtrer les articles par langue d'origine",
            "distinguer les sources francophones des anglophones"
        ],
        "avoid_for": ["analyse de contenu ou de tonalité"],
        "data_type": "texte code langue",
        "example_values": ["fr", "en", "pt"],
        "synonyms": ["langue", "langue source", "langue article", "francophone", "anglophone"],
        "aggregation_hint": "GROUP BY source_language ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE source_language = 'fr' pour sources francophones.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie dérivée de TranslationInfo."
    },

    "is_translated": {
        "business_name": "Article traduit",
        "origin": "enriched",
        "definition": "Booléen indiquant si l'article a été traduit par GDELT depuis une autre langue. Dérivé de TranslationInfo.",
        "use_for": [
            "filtrer les articles traduits ou originaux",
            "analyser la proportion d'articles traduits"
        ],
        "avoid_for": ["analyse de tonalité ou de volume"],
        "data_type": "BOOLEAN",
        "example_values": ["TRUE", "FALSE"],
        "synonyms": ["traduit", "translation", "article traduit"],
        "aggregation_hint": "WHERE is_translated = TRUE pour les articles traduits.",
        "filters_hint": "WHERE is_translated = FALSE pour les articles originaux.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus lisible que TranslationInfo brut."
    },

    # ============================================================
    # COLONNES DE COMPTAGE ENRICHIES
    # ============================================================

    "nb_themes": {
        "business_name": "Nombre de thèmes dans l'article",
        "origin": "enriched",
        "definition": "Nombre de thèmes distincts détectés dans l'article. Calculé en comptant les éléments de V2Themes.",
        "use_for": [
            "mesurer la richesse thématique d'un article",
            "filtrer les articles multi-thèmes",
            "proxy de richesse éditoriale"
        ],
        "avoid_for": ["comptage des occurrences d'un thème spécifique"],
        "data_type": "entier",
        "example_values": ["3", "12", "25"],
        "synonyms": ["nombre thèmes", "richesse thématique", "diversité thèmes"],
        "aggregation_hint": "AVG(nb_themes) pour richesse thématique moyenne. WHERE nb_themes > 10 pour articles riches en thèmes.",
        "filters_hint": "WHERE nb_themes > 5 pour articles avec plusieurs thèmes.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Ne donne pas la liste des thèmes. Pour les thèmes précis, utiliser UNNEST(SPLIT(V2Themes, ';'))."
    },

    "nb_persons": {
        "business_name": "Nombre de personnes citées dans l'article",
        "origin": "enriched",
        "definition": "Nombre de personnes distinctes mentionnées dans l'article. Calculé en comptant les éléments de V2Persons.",
        "use_for": [
            "mesurer la densité de personnalités dans un article",
            "filtrer les articles citant beaucoup de personnes"
        ],
        "avoid_for": ["identifier les personnes précises (utiliser UNNEST(SPLIT(V2Persons, ';')))"],
        "data_type": "entier",
        "example_values": ["0", "2", "8"],
        "synonyms": ["nombre personnes", "densité personnalités"],
        "aggregation_hint": "AVG(nb_persons) pour la moyenne. WHERE nb_persons > 3 pour les articles citant plusieurs personnalités.",
        "filters_hint": "WHERE nb_persons > 0 pour les articles citant au moins une personne.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Pour identifier les personnes précises, utiliser UNNEST(SPLIT(V2Persons, ';')) AS person."
    },

    "nb_organizations": {
        "business_name": "Nombre d'organisations citées dans l'article",
        "origin": "enriched",
        "definition": "Nombre d'organisations distinctes mentionnées dans l'article. Calculé en comptant les éléments de V2Organizations.",
        "use_for": [
            "mesurer la densité institutionnelle d'un article",
            "filtrer les articles citant plusieurs organisations"
        ],
        "avoid_for": ["identifier les organisations précises (utiliser UNNEST(SPLIT(V2Organizations, ';')))"],
        "data_type": "entier",
        "example_values": ["0", "3", "10"],
        "synonyms": ["nombre organisations", "institutions mentionnées"],
        "aggregation_hint": "AVG(nb_organizations) pour la moyenne.",
        "filters_hint": "WHERE nb_organizations > 2 pour les articles citant plusieurs organisations.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Pour les organisations précises, utiliser UNNEST(SPLIT(V2Organizations, ';')) AS org."
    },

    "nb_locations": {
        "business_name": "Nombre de lieux mentionnés dans l'article",
        "origin": "enriched",
        "definition": "Nombre de lieux géographiques distincts détectés dans l'article. Calculé en comptant les éléments de V2Locations.",
        "use_for": [
            "mesurer la couverture géographique d'un article",
            "filtrer les articles multi-localisations"
        ],
        "avoid_for": ["géographie fine des événements"],
        "data_type": "entier",
        "example_values": ["0", "2", "5"],
        "synonyms": ["nombre lieux", "couverture géographique article"],
        "aggregation_hint": "AVG(nb_locations) pour la moyenne.",
        "filters_hint": "WHERE nb_locations > 0 pour les articles géolocalisés.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Pour les lieux précis, utiliser UNNEST(SPLIT(V2Locations, ';')) AS location."
    },

    "is_rich_article": {
        "business_name": "Article riche",
        "origin": "enriched",
        "definition": "Booléen indiquant si l'article est considéré comme riche éditorialement selon des critères combinés : word_count élevé, nb_themes élevé, nb_persons > 0 ou nb_organizations > 0. Permet de filtrer les articles substantiels des articles courts ou vides.",
        "use_for": [
            "filtrer uniquement les articles à contenu substantiel",
            "réduire le bruit dans les analyses thématiques",
            "analyser les articles riches en tonalité ou en thèmes"
        ],
        "avoid_for": ["analyse de volume global"],
        "data_type": "BOOLEAN",
        "example_values": ["TRUE", "FALSE"],
        "synonyms": [
            "article riche", "article substantiel",
            "article long", "contenu riche", "article de fond"
        ],
        "aggregation_hint": "WHERE is_rich_article = TRUE pour filtrer les articles riches.",
        "filters_hint": "WHERE is_rich_article = TRUE.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Le critère exact dépend de ton pipeline d'enrichissement. C'est le filtre standard pour les questions sur les 'articles riches', 'articles de fond', 'articles substantiels'."
    }
}



# à ajouter dans assistant/metadata/column_dictionary.py

MENTIONS_CLEAN_METADATA = {

    # ============================================================
    # IDENTIFIANTS ET JOINTURES — GDELT NATIF
    # ============================================================

    "GLOBALEVENTID": {
        "business_name": "Identifiant de l'événement mentionné",
        "origin": "gdelt_native",
        "definition": "Identifiant unique de l'événement GDELT auquel cette mention se rapporte. Permet de relier chaque mention à son événement parent dans events_clean. C'est la clé de jointure principale entre mentions_clean et events_clean.",
        "use_for": [
            "joindre mentions_clean avec events_clean",
            "compter le nombre de mentions par événement",
            "relier la couverture médiatique à un événement précis"
        ],
        "avoid_for": [
            "filtrage par plage numérique",
            "calculs numériques",
            "jointure avec gkg_clean"
        ],
        "data_type": "identifiant entier",
        "example_values": ["1082895024", "1082895025"],
        "synonyms": ["événement mentionné", "id événement", "event id"],
        "aggregation_hint": "GROUP BY GLOBALEVENTID pour compter les mentions par événement. COUNT(DISTINCT GLOBALEVENTID) pour compter les événements ayant au moins une mention.",
        "filters_hint": "Ne pas filtrer par plage numérique. Utiliser les colonnes de date pour filtrer dans le temps.",
        "join_role": "Clé de jointure principale avec events_clean.GLOBALEVENTID. Jointure standard : mentions_clean.GLOBALEVENTID = events_clean.GLOBALEVENTID. NE JAMAIS joindre à une colonne de date.",
        "notes": "C'est la SEULE clé de jointure entre mentions_clean et events_clean. Ne jamais joindre GLOBALEVENTID à MentionTimeDate ni à aucune colonne de date."
    },

    # ============================================================
    # DATES — GDELT NATIF
    # ============================================================

    "MentionTimeDate": {
        "business_name": "Date-heure brute de la mention (entier)",
        "origin": "gdelt_native",
        "definition": "Date et heure à laquelle la mention de l'événement a été publiée ou détectée, au format entier brut YYYYMMDDHHMMSS. C'est une date technique d'ingestion.",
        "use_for": ["vérifications techniques"],
        "avoid_for": [
            "filtrage temporel métier",
            "agrégations temporelles",
            "jointure avec GLOBALEVENTID"
        ],
        "data_type": "entier brut datetime",
        "example_values": ["20250115120000", "20250622094500"],
        "synonyms": [],
        "aggregation_hint": "Toujours préférer mention_date (DATE) ou mention_year_month (STRING) pour les analyses temporelles.",
        "filters_hint": "Préférer mention_date ou mention_year_month.",
        "join_role": "AUCUN. NE JAMAIS joindre MentionTimeDate à GLOBALEVENTID ni à aucun identifiant.",
        "notes": "Colonne brute GDELT. Ne jamais utiliser pour une jointure. Toujours préférer mention_date ou mention_year_month pour les analyses métier."
    },

    # ============================================================
    # TYPE ET SOURCE — GDELT NATIF
    # ============================================================

    "MentionType": {
        "business_name": "Type de source de la mention (entier brut)",
        "origin": "gdelt_native",
        "definition": "Code entier GDELT indiquant le type de source ayant produit la mention. Valeurs : 1 = Web, 2 = Citation, 3 = Core, 4 = Drudge, 5 = Syndicated, 6 = National Broadcast, 7 = Newspaper.",
        "use_for": ["vérifications techniques du type de source"],
        "avoid_for": [
            "affichage lisible du type de source",
            "filtrage métier par type de source"
        ],
        "data_type": "entier code (1-7)",
        "example_values": ["1", "6", "7"],
        "synonyms": [],
        "aggregation_hint": "Préférer MentionType_Label (enrichi) pour les analyses et l'affichage.",
        "filters_hint": "Préférer WHERE MentionType_Label = 'Web' pour un filtrage lisible.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. Toujours préférer MentionType_Label pour les analyses métier."
    },

    "MentionSourceName": {
        "business_name": "Nom de la source médiatique",
        "origin": "gdelt_native",
        "definition": "Nom ou domaine du média, site web ou source ayant publié la mention de l'événement. C'est la référence principale pour identifier quel média parle d'un événement.",
        "use_for": [
            "identifier les médias qui couvrent les événements",
            "top médias par volume de couverture",
            "analyser la diversité des sources médiatiques",
            "comparer les sources par tonalité ou confiance"
        ],
        "avoid_for": [
            "analyse des articles GKG (préférer SourceCommonName dans gkg_clean)",
            "comptage d'articles (préférer gkg_clean)"
        ],
        "data_type": "texte",
        "example_values": ["bbc.com", "rfi.fr", "24haubenin.com", "voaafrique.com"],
        "synonyms": [
            "média", "source", "journal", "site",
            "médias qui parlent", "sources médiatiques",
            "qui couvre", "couverture par source"
        ],
        "aggregation_hint": "GROUP BY MentionSourceName ORDER BY COUNT(*) DESC LIMIT 10 pour le top des médias qui parlent le plus des événements.",
        "filters_hint": "WHERE MentionSourceName LIKE '%rfi%' pour filtrer un média spécifique.",
        "join_role": "Aucun.",
        "notes": "C'est la colonne à utiliser pour toute question sur 'quels médias parlent le plus'. Différent de SourceCommonName dans gkg_clean qui concerne les articles GKG."
    },

    "Confidence": {
        "business_name": "Score de confiance de la mention",
        "origin": "gdelt_native",
        "definition": "Score entier entre 0 et 100 indiquant le niveau de confiance de GDELT dans la détection et la classification de cette mention. Un score élevé signifie que GDELT est très sûr de l'association entre la mention et l'événement.",
        "use_for": [
            "filtrer les mentions les plus fiables",
            "analyser la fiabilité des mentions par source",
            "comparer la confiance entre types de sources"
        ],
        "avoid_for": [
            "mesurer la couverture médiatique en volume",
            "mesurer la tonalité",
            "proxy de popularité ou d'importance d'un événement"
        ],
        "data_type": "entier [0, 100]",
        "example_values": ["40", "65", "90"],
        "synonyms": [
            "confiance", "fiabilité", "qualité mention",
            "score confiance", "reliability"
        ],
        "aggregation_hint": "AVG(Confidence) pour la confiance moyenne par groupe. WHERE Confidence >= 60 pour les mentions fiables.",
        "filters_hint": "WHERE Confidence >= 50 pour les mentions de confiance moyenne ou haute.",
        "join_role": "Aucun.",
        "notes": "NE JAMAIS utiliser Confidence comme mesure de couverture médiatique. La couverture médiatique se mesure avec COUNT(*) sur les mentions, pas avec AVG(Confidence). Confidence mesure la qualité de la détection, pas le volume."
    },

    "MentionDocTone": {
        "business_name": "Tonalité du document de la mention",
        "origin": "gdelt_native",
        "definition": "Score de tonalité du document source ayant produit cette mention. Valeurs négatives = document à tonalité négative, valeurs positives = document positif. Mesure le sentiment de l'article source de la mention.",
        "use_for": [
            "analyser la tonalité des mentions par événement",
            "comparer la tonalité des couvertures entre sources",
            "mesurer la perception médiatique d'un événement",
            "tonalité moyenne des mentions par catégorie d'événement"
        ],
        "avoid_for": [
            "mesurer la gravité géopolitique (préférer GoldsteinScale dans events_clean)",
            "mesurer la couverture en volume"
        ],
        "data_type": "float",
        "example_values": ["-5.2", "-1.3", "0.0", "+2.8"],
        "synonyms": [
            "tonalité mention", "tonalité document",
            "sentiment mention", "ton des médias",
            "tonalité des mentions", "tonalité par source"
        ],
        "aggregation_hint": "AVG(MentionDocTone) pour la tonalité moyenne des mentions. GROUP BY EventCategory pour la tonalité par catégorie d'événement.",
        "filters_hint": "WHERE MentionDocTone < 0 pour les mentions à tonalité négative.",
        "join_role": "Aucun.",
        "notes": "NE PAS confondre avec AvgTone (tonalité des événements dans events_clean) ni avec tone (tonalité des articles dans gkg_clean). MentionDocTone concerne la tonalité de chaque mention individuelle dans mentions_clean."
    },

    "MentionDocTranslationInfo": {
        "business_name": "Informations de traduction du document de la mention",
        "origin": "gdelt_native",
        "definition": "Informations brutes sur la traduction du document source de la mention si applicable. Contient le code langue source.",
        "use_for": ["vérification technique de la traduction"],
        "avoid_for": ["analyses de contenu ou de tonalité"],
        "data_type": "texte",
        "example_values": ["srclc:fr", "srclc:en", ""],
        "synonyms": ["traduction mention"],
        "aggregation_hint": "Préférer les colonnes enrichies is_translated et source_language.",
        "filters_hint": "Préférer WHERE is_translated = TRUE.",
        "join_role": "Aucun.",
        "notes": "Colonne brute. Toujours utiliser is_translated (BOOLEAN) et source_language (STRING) pour les analyses."
    },

    # ============================================================
    # DATES ENRICHIES
    # ============================================================

    "mention_datetime": {
        "business_name": "Timestamp précis de la mention",
        "origin": "enriched",
        "definition": "Timestamp TIMESTAMP au format YYYY-MM-DD HH:MM:SS dérivé de MentionTimeDate. Référence temporelle précise à la seconde pour les mentions.",
        "use_for": [
            "analyses temporelles précises à l'heure",
            "ordonnancement chronologique des mentions"
        ],
        "avoid_for": ["agrégations mensuelles (préférer mention_year_month)"],
        "data_type": "TIMESTAMP",
        "example_values": ["2025-01-15 12:00:00", "2025-06-22 09:45:00"],
        "synonyms": ["date heure mention", "timestamp mention"],
        "aggregation_hint": "EXTRACT(HOUR FROM mention_datetime) pour analyses horaires.",
        "filters_hint": "WHERE mention_datetime >= '2025-01-01' AND mention_datetime < '2025-04-01'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. NE JAMAIS joindre mention_datetime à GLOBALEVENTID."
    },

    "mention_date": {
        "business_name": "Date de la mention",
        "origin": "enriched",
        "definition": "Date de publication de la mention au format DATE SQL propre (YYYY-MM-DD), dérivée de MentionTimeDate. Référence temporelle journalière pour les mentions.",
        "use_for": [
            "filtrage journalier des mentions",
            "agrégations journalières",
            "comparaisons de dates"
        ],
        "avoid_for": ["agrégations mensuelles (préférer mention_year_month)"],
        "data_type": "DATE",
        "example_values": ["2025-01-15", "2025-06-22"],
        "synonyms": ["date mention", "date publication mention"],
        "aggregation_hint": "GROUP BY mention_date pour analyses journalières.",
        "filters_hint": "WHERE EXTRACT(YEAR FROM mention_date) = 2025. WHERE mention_date BETWEEN '2025-01-01' AND '2025-03-31'.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Toujours préférer mention_date à MentionTimeDate (entier brut) pour les filtres temporels."
    },

    "mention_year_month": {
        "business_name": "Mois-Année de la mention",
        "origin": "enriched",
        "definition": "Représentation mensuelle de la date de la mention au format STRING 'YYYY-MM'. C'est la référence pour toute agrégation mensuelle sur les mentions.",
        "use_for": [
            "agrégations mensuelles des mentions",
            "séries temporelles mensuelles de la couverture médiatique",
            "évolution mois par mois du volume de mentions",
            "filtrage de périmètre sur l'année 2025"
        ],
        "avoid_for": ["analyses journalières"],
        "data_type": "STRING format YYYY-MM",
        "example_values": ["2025-01", "2025-06", "2025-12"],
        "synonyms": [
            "mois", "mensuel", "par mois",
            "évolution mensuelle", "période mensuelle"
        ],
        "aggregation_hint": "GROUP BY mention_year_month ORDER BY mention_year_month pour série temporelle mensuelle des mentions.",
        "filters_hint": "WHERE mention_year_month LIKE '2025-%' pour toute l'année. WHERE mention_year_month = '2025-01' pour janvier.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. C'est LE filtre temporel standard pour mentions_clean, équivalent à Year = 2025 pour events_clean et à gkg_year_month LIKE '2025-%' pour gkg_clean."
    },

    # ============================================================
    # COLONNES ENRICHIES
    # ============================================================

    "MentionType_Label": {
        "business_name": "Libellé du type de source de la mention",
        "origin": "enriched",
        "definition": "Version texte lisible de MentionType. Valeurs : 'Web', 'Citation', 'Core', 'Drudge Report', 'Syndicated', 'National Broadcast', 'Newspaper'.",
        "use_for": [
            "analyser la répartition des mentions par type de source",
            "filtrer par type de source en langage métier",
            "distinguer les sources web, broadcast, presse écrite"
        ],
        "avoid_for": ["calculs numériques sur le type"],
        "data_type": "texte",
        "example_values": [
            "Web", "National Broadcast",
            "Newspaper", "Syndicated"
        ],
        "synonyms": [
            "type source", "type média", "type mention",
            "web", "radio", "télévision", "presse"
        ],
        "aggregation_hint": "GROUP BY MentionType_Label ORDER BY COUNT(*) DESC pour répartition par type de source.",
        "filters_hint": "WHERE MentionType_Label = 'Web' pour les mentions web. WHERE MentionType_Label = 'National Broadcast' pour la radio/TV.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Toujours préférer MentionType_Label à MentionType (entier) pour les questions métier sur le type de source."
    },

    "tone_category": {
        "business_name": "Catégorie de tonalité de la mention",
        "origin": "enriched",
        "definition": "Catégorie textuelle de la tonalité de la mention, dérivée de MentionDocTone. Valeurs : 'Très négatif', 'Négatif', 'Neutre', 'Positif', 'Très positif'.",
        "use_for": [
            "analyser la répartition des mentions par tonalité",
            "filtrer les mentions à tonalité négative ou positive",
            "affichage lisible de la tonalité des mentions"
        ],
        "avoid_for": ["calculs numériques sur la tonalité (préférer MentionDocTone)"],
        "data_type": "texte catégorie",
        "example_values": [
            "Très négatif", "Négatif", "Neutre",
            "Positif", "Très positif"
        ],
        "synonyms": [
            "tonalité mention", "catégorie tonalité",
            "sentiment mention", "mentions négatives", "mentions positives"
        ],
        "aggregation_hint": "GROUP BY tone_category ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE tone_category = 'Très négatif' ou WHERE tone_category IN ('Négatif', 'Très négatif').",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer tone_category pour l'affichage et les filtres métier. Utiliser AVG(MentionDocTone) pour les calculs numériques de tonalité."
    },

    "confidence_level": {
        "business_name": "Niveau de confiance de la mention",
        "origin": "enriched",
        "definition": "Catégorie textuelle du score de confiance, dérivée de Confidence. Valeurs typiques : 'Faible' (0-33), 'Moyen' (34-66), 'Élevé' (67-100).",
        "use_for": [
            "filtrer les mentions par niveau de fiabilité",
            "analyser la répartition de la confiance par source",
            "affichage lisible de la fiabilité"
        ],
        "avoid_for": [
            "mesure de couverture médiatique",
            "calculs numériques précis (préférer Confidence)"
        ],
        "data_type": "texte catégorie",
        "example_values": ["Faible", "Moyen", "Élevé"],
        "synonyms": [
            "niveau confiance", "fiabilité", "qualité mention",
            "confiance élevée", "mentions fiables"
        ],
        "aggregation_hint": "GROUP BY confidence_level ORDER BY COUNT(*) DESC. WHERE confidence_level = 'Élevé' pour les mentions les plus fiables.",
        "filters_hint": "WHERE confidence_level = 'Élevé' pour filtrer les mentions fiables.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Préférer confidence_level pour l'affichage. Utiliser AVG(Confidence) pour les calculs numériques. NE JAMAIS utiliser comme proxy de couverture médiatique."
    },

    "source_language": {
        "business_name": "Langue de la source de la mention",
        "origin": "enriched",
        "definition": "Code de la langue de l'article source ayant produit la mention, avant traduction éventuelle. Dérivé de MentionDocTranslationInfo.",
        "use_for": [
            "analyser la diversité linguistique des sources de mentions",
            "filtrer les mentions par langue",
            "distinguer couverture francophone vs anglophone"
        ],
        "avoid_for": ["analyse de contenu ou de tonalité"],
        "data_type": "texte code langue",
        "example_values": ["fr", "en", "pt"],
        "synonyms": [
            "langue source", "langue mention",
            "francophone", "anglophone", "langue"
        ],
        "aggregation_hint": "GROUP BY source_language ORDER BY COUNT(*) DESC.",
        "filters_hint": "WHERE source_language = 'fr' pour les mentions de sources francophones.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Dérivée de MentionDocTranslationInfo."
    },

    "is_translated": {
        "business_name": "Mention traduite",
        "origin": "enriched",
        "definition": "Booléen indiquant si le document source de la mention a été traduit par GDELT depuis une autre langue. Dérivé de MentionDocTranslationInfo.",
        "use_for": [
            "distinguer les mentions d'articles originaux vs traduits",
            "analyser la proportion de couverture traduite"
        ],
        "avoid_for": ["analyse de tonalité ou de volume"],
        "data_type": "BOOLEAN",
        "example_values": ["TRUE", "FALSE"],
        "synonyms": ["traduit", "mention traduite", "article traduit"],
        "aggregation_hint": "WHERE is_translated = FALSE pour les mentions de sources originales.",
        "filters_hint": "WHERE is_translated = TRUE pour les mentions traduites.",
        "join_role": "Aucun.",
        "notes": "Colonne enrichie. Plus lisible que MentionDocTranslationInfo brut."
    }
}



# ============================================================
# EXPORT PRINCIPAL — utilisé par schema_retriever.py
# ============================================================

COLUMN_METADATA = {
    "events_clean":   EVENTS_CLEAN_METADATA,
    "gkg_clean":      GKG_CLEAN_METADATA,
    "mentions_clean": MENTIONS_CLEAN_METADATA,
}