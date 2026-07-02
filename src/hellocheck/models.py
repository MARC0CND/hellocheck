from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SapCommand:
    row_number: int
    tcode: Optional[str]
    field_id: Optional[str]
    value: Optional[str]
    action: Optional[str]


@dataclass
class SapConfig:
    backend: str
    connection_index: int
    session_index: int
    dry_run: bool = False
