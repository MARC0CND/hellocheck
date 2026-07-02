from __future__ import annotations

import json
from pathlib import Path

from .models import SapConfig


def load_config(path: Path, cli_backend: str | None, cli_dry_run: bool) -> SapConfig:
    raw: dict[str, object] = {}
    if path.exists():
        raw = json.loads(path.read_text(encoding="utf-8"))

    backend = (cli_backend or str(raw.get("backend", "comtypes"))).lower()
    if backend not in {"comtypes", "pywin32"}:
        raise ValueError("backend must be one of: comtypes, pywin32")

    connection_index = int(raw.get("connection_index", 0))
    session_index = int(raw.get("session_index", 0))
    dry_run = bool(raw.get("dry_run", False)) or cli_dry_run

    return SapConfig(
        backend=backend,
        connection_index=connection_index,
        session_index=session_index,
        dry_run=dry_run,
    )
