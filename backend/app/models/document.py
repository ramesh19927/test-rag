"""Document model used throughout the platform."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Document:
    """Structured representation of an input document."""

    id: str
    name: str
    source_path: str
    raw_text: str
    cleaned_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)
