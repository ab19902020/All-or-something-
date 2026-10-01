from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Literal

Status = Literal["draft", "review", "approved"]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class EpisodeProject:
    title: str
    status: Status = "draft"
    director_notes: str = ""
    production_notes: str = ""
    style_references: list[str] = field(default_factory=list)
    character_assets: list[str] = field(default_factory=list)
    background_assets: list[str] = field(default_factory=list)
    voiceovers: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)

    @property
    def final_master_approved(self) -> bool:
        return self.status == "approved"

    def mark_draft(self) -> None:
        self.status = "draft"
        self.updated_at = _now()

    def mark_review(self) -> None:
        self.status = "review"
        self.updated_at = _now()

    def approve_final_master(self) -> None:
        self.status = "approved"
        self.updated_at = _now()

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "EpisodeProject":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)
