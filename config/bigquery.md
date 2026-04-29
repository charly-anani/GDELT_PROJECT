# BigQuery Connection

## Identifiants de projet

| Champ | Valeur |
| --- | --- |
| Project ID | `gdelt-494812` |
| Dataset | `benin_2025` |
| Source de vérité | BigQuery |

## Accès recommandé

- Authentification locale : Application Default Credentials ou compte de service.
- Ne jamais stocker de clés privées dans le dépôt.
- Garder les secrets dans l'environnement local ou un gestionnaire de secrets.

## Convention d'utilisation

- Les requêtes d'extraction vivent dans `sql/01_extract_*.sql`.
- Les requêtes de préparation vivent dans `sql/04_clean_enrich_*.sql`.
- Les couches de données brutes, nettoyées et enrichies restent dans BigQuery.

## Notes

- Si des noms de tables BigQuery réels diffèrent de ceux attendus dans les requêtes, les fichiers SQL doivent être ajustés pour correspondre à la structure du dataset `benin_2025`.