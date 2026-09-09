from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from uuid import uuid4


class ReportStore:
    def __init__(self, db_path: str | Path, enabled: bool = True) -> None:
        self.enabled = enabled
        self.db_path = Path(db_path)
        if not self.enabled:
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                create table if not exists reports (
                    id text primary key,
                    source_name text,
                    patient_hash text,
                    summary text,
                    payload text not null,
                    created_at timestamp default current_timestamp
                )
                """
            )

    def save(self, payload: dict, source_name: str | None = None, patient_hash: str | None = None) -> str:
        if not self.enabled:
            raise RuntimeError("report persistence is disabled")
        report_id = str(uuid4())
        with self._connect() as con:
            con.execute(
                "insert into reports(id, source_name, patient_hash, summary, payload) values (?, ?, ?, ?, ?)",
                (report_id, source_name, patient_hash, payload.get("summary"), json.dumps(payload)),
            )
        return report_id

    def get(self, report_id: str) -> dict | None:
        if not self.enabled:
            return None
        with self._connect() as con:
            row = con.execute("select payload from reports where id = ?", (report_id,)).fetchone()
        return json.loads(row[0]) if row else None

    def latest(self) -> dict | None:
        if not self.enabled:
            return None
        with self._connect() as con:
            row = con.execute(
                "select payload from reports order by created_at desc, id desc limit 1"
            ).fetchone()
        return json.loads(row[0]) if row else None
