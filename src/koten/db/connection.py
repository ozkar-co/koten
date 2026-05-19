from __future__ import annotations

import sqlite3
from pathlib import Path

from koten.core.config import settings


def get_connection() -> sqlite3.Connection:
    db_path = Path(settings.db_file)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
