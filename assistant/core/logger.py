# assistant/core/logger.py

import csv
import os
from datetime import datetime
from typing import Optional


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "assistant_interactions.csv")


def ensure_log_dir() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)


def log_interaction(
    user_question: str,
    sql: Optional[str],
    status: str,
    row_count: Optional[int] = None,
    time_seconds: Optional[float] = None,
    error: Optional[str] = None,
) -> None:
    """
    Enregistre une interaction dans un CSV.
    Colonnes :
    - timestamp
    - user_question
    - sql
    - status
    - row_count
    - time_seconds
    - error
    """

    ensure_log_dir()
    file_exists = os.path.exists(LOG_FILE)

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "timestamp",
                "user_question",
                "sql",
                "status",
                "row_count",
                "time_seconds",
                "error",
            ])

        writer.writerow([
            datetime.utcnow().isoformat(),
            user_question,
            sql or "",
            status,
            row_count if row_count is not None else "",
            f"{time_seconds:.4f}" if time_seconds is not None else "",
            error or "",
        ])