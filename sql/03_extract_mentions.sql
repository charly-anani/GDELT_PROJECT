-- Extraction BigQuery des mentions GDELT
-- Projet : gdelt-494812
-- Dataset : benin_2025
-- Paramètres attendus:
--   @start_date
--   @end_date

SELECT
  *
FROM `gdelt-494812.benin_2025.mentions`
WHERE DATE(record_date) BETWEEN @start_date AND @end_date;