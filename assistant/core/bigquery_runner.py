# assistant/core/bigquery_runner.py

from typing import Any, Dict, Tuple
import time

import pandas as pd
from google.cloud import bigquery

from assistant.core.config import BQ_PROJECT


class BigQueryRunner:
    def __init__(self, project: str = BQ_PROJECT):
        self.client = bigquery.Client(project=project)

    def run_query(self, sql: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Exécute une requête SQL sur BigQuery et renvoie :
        - le DataFrame des résultats,
        - un dict de métadonnées (temps, nombre de lignes, job_id).
        """
        start = time.time()
        job = self.client.query(sql)
        result = job.result()
        df = result.to_dataframe()
        end = time.time()

        metadata = {
            "job_id": job.job_id,
            "time_seconds": end - start,
            "row_count": len(df),
        }

        return df, metadata