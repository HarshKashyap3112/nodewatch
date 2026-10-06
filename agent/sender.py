import json
import logging
import sqlite3
import time
from typing import Any, Dict, List
import httpx
from config import AgentConfig

logger = logging.getLogger(__name__)


class MetricSender:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.ingest_url = f"{config.server_url}/api/v1/metrics/ingest"
        self.headers = {"X-Agent-API-Key": config.api_key, "Content-Type": "application/json"}
        self._init_buffer_db()

    def _init_buffer_db(self):
        conn = sqlite3.connect(self.config.buffer_db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS buffered_payloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                payload_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()

    def buffer_payload(self, payload: Dict[str, Any]):
        try:
            conn = sqlite3.connect(self.config.buffer_db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO buffered_payloads (payload_json, created_at) VALUES (?, ?)",
                (json.dumps(payload), time.time())
            )
            conn.commit()
            conn.close()
            logger.warning("Collector unreachable. Payload buffered locally.")
        except Exception as e:
            logger.error(f"Failed to buffer payload locally: {e}")

    def flush_buffer(self):
        try:
            conn = sqlite3.connect(self.config.buffer_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, payload_json FROM buffered_payloads ORDER BY id ASC LIMIT 50")
            rows = cursor.fetchall()
            if not rows:
                conn.close()
                return

            logger.info(f"Attempting to flush {len(rows)} buffered payloads to collector...")
            failed_ids = []
            for item_id, payload_str in rows:
                payload = json.loads(payload_str)
                try:
                    with httpx.Client(timeout=10.0) as client:
                        resp = client.post(self.ingest_url, json=payload, headers=self.headers)
                        if resp.is_success:
                            cursor.execute("DELETE FROM buffered_payloads WHERE id = ?", (item_id,))
                            conn.commit()
                        else:
                            failed_ids.append(item_id)
                            break
                except Exception:
                    failed_ids.append(item_id)
                    break

            conn.close()
        except Exception as e:
            logger.error(f"Error while flushing buffered payloads: {e}")

    def send_payload(self, payload: Dict[str, Any]) -> bool:
        # First attempt to flush any previously buffered payloads
        self.flush_buffer()

        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(self.ingest_url, json=payload, headers=self.headers)
                if resp.is_success:
                    logger.info("Successfully pushed metrics payload to collector.")
                    return True
                else:
                    logger.error(f"Collector returned error {resp.status_code}: {resp.text}")
                    self.buffer_payload(payload)
                    return False
        except Exception as e:
            logger.error(f"Network error connecting to collector ({self.ingest_url}): {e}")
            self.buffer_payload(payload)
            return False
