## Accès recommandé

- Authentification locale via Application Default Credentials — exécuter la commande suivante :
  ```bash
  gcloud auth application-default login
  ```
- Le compte `formations@isheero.com` a été ajouté au projet `gdelt-494812` avec les rôles suivants :

| Rôle | Niveau | Utilité |
| --- | --- | --- |
| `Lecteur de données BigQuery` | Projet | Permet de lire toutes les tables de tous les datasets du projet `gdelt-494812`, y compris `benin_2025` |
| `Utilisateur de job BigQuery` | Projet | Permet d'exécuter des requêtes (lancer des jobs) sur le projet |