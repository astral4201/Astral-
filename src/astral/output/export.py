"""JSON export for ConfluenceResult."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any

from astral.core.models import ConfluenceResult


def _serialize(obj: Any) -> Any:
    """Recursively serialize dataclasses, enums, dates."""
    if is_dataclass(obj):
        return {k: _serialize(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Enum):
        return obj.value if hasattr(obj, "value") else obj.name
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize(i) for i in obj]
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return obj


def result_to_dict(result: ConfluenceResult) -> dict:
    """Convert a ConfluenceResult to a JSON-serializable dict."""
    return _serialize(result)


def result_to_json(result: ConfluenceResult, indent: int = 2) -> str:
    """Convert a ConfluenceResult to a JSON string."""
    return json.dumps(result_to_dict(result), indent=indent, ensure_ascii=False, default=str)


def export_to_file(result: ConfluenceResult, filepath: str) -> None:
    """Export result to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result_to_json(result))
