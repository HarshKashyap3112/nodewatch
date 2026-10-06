import json
import os
from typing import Dict, List, Optional


class AgentConfig:
    def __init__(
        self,
        server_url: str = "http://localhost:8000",
        api_key: str = "",
        interval: int = 30,
        buffer_db_path: str = "agent_buffer.db",
        process_checks: Optional[List[str]] = None,
        port_checks: Optional[List[int]] = None
    ):
        self.server_url = server_url.rstrip("/")
        self.api_key = api_key
        self.interval = interval
        self.buffer_db_path = buffer_db_path
        self.process_checks = process_checks or []
        self.port_checks = port_checks or []

    @classmethod
    def load_from_file(cls, filepath: str) -> "AgentConfig":
        if not os.path.exists(filepath):
            return cls()
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            server_url=data.get("server_url", "http://localhost:8000"),
            api_key=data.get("api_key", ""),
            interval=data.get("interval", 30),
            buffer_db_path=data.get("buffer_db_path", "agent_buffer.db"),
            process_checks=data.get("process_checks", []),
            port_checks=data.get("port_checks", [])
        )
