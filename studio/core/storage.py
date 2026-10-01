from __future__ import annotations

import json
import os
import re
import shutil
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .project import EpisodeProject


ASSET_KINDS = {
    "style": "style_references",
    "character": "character_assets",
    "background": "background_assets",
    "voiceover": "voiceovers",
}


def safe_name(value: str) -> str:
    value = Path(value).name
    value = re.sub(r"[^A-Za-z0-9._ -]+", "_", value).strip(" .")
    return value or f"asset-{uuid.uuid4().hex[:8]}"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:64] or f"episode-{uuid.uuid4().hex[:8]}"


class ProjectStore:
    def __init__(self, root: str | Path | None = None):
        configured = root or os.environ.get("URS_WORKSPACE")
        self.root = Path(configured or (Path.home() / "UnitedRoadStudio"))
        self.projects_dir = self.root / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def create(self, title: str) -> tuple[str, EpisodeProject]:
        base = slugify(title)
        project_id = base
        n = 2
        while (self.projects_dir / project_id).exists():
            project_id = f"{base}-{n}"
            n += 1
        project = EpisodeProject(title=title)
        pdir = self.project_dir(project_id)
        for folder in ("style", "characters", "backgrounds", "voiceovers", "transcripts", "plans", "renders", "qa"):
            (pdir / folder).mkdir(parents=True, exist_ok=True)
        self.save(project_id, project)
        self.write_settings(project_id, {
            "director_mode": "local",
            "ollama_url": "http://127.0.0.1:11434",
            "director_model": "qwen2.5:7b",
            "vision_model": "qwen2.5vl:7b",
            "whisper_model": "small.en",
            "renderer": "auto",
            "legacy_root": "",
            "legacy_scene": "",
        })
        return project_id, project

    def list(self) -> list[dict]:
        out = []
        for pdir in sorted(self.projects_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not pdir.is_dir() or not (pdir / "project.json").exists():
                continue
            try:
                project = EpisodeProject.load(pdir / "project.json")
            except Exception:
                continue
            out.append({"id": pdir.name, **asdict(project)})
        return out

    def project_dir(self, project_id: str) -> Path:
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", project_id):
            raise ValueError("Invalid project id")
        return self.projects_dir / project_id

    def load(self, project_id: str) -> EpisodeProject:
        path = self.project_dir(project_id) / "project.json"
        if not path.exists():
            raise FileNotFoundError(project_id)
        return EpisodeProject.load(path)

    def save(self, project_id: str, project: EpisodeProject) -> None:
        project.save(self.project_dir(project_id) / "project.json")

    def settings_path(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "settings.json"

    def read_settings(self, project_id: str) -> dict:
        path = self.settings_path(project_id)
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def write_settings(self, project_id: str, settings: dict) -> None:
        path = self.settings_path(project_id)
        path.write_text(json.dumps(settings, indent=2), encoding="utf-8")

    def add_asset(self, project_id: str, kind: str, source: str | Path, original_name: str) -> str:
        if kind not in ASSET_KINDS:
            raise ValueError(f"Unsupported asset kind: {kind}")
        folder = {
            "style": "style",
            "character": "characters",
            "background": "backgrounds",
            "voiceover": "voiceovers",
        }[kind]
        dest_dir = self.project_dir(project_id) / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = safe_name(original_name)
        dest = dest_dir / filename
        stem, suffix = dest.stem, dest.suffix
        i = 2
        while dest.exists():
            dest = dest_dir / f"{stem}-{i}{suffix}"
            i += 1
        shutil.copy2(source, dest)

        project = self.load(project_id)
        attr = ASSET_KINDS[kind]
        values = list(getattr(project, attr))
        values.append(str(dest.relative_to(self.project_dir(project_id))))
        setattr(project, attr, values)
        self.save(project_id, project)
        return str(dest.relative_to(self.project_dir(project_id)))

    def asset_paths(self, project_id: str, kind: str) -> list[Path]:
        project = self.load(project_id)
        attr = ASSET_KINDS[kind]
        return [self.project_dir(project_id) / rel for rel in getattr(project, attr)]

    def media_path(self, project_id: str, relative: str) -> Path:
        base = self.project_dir(project_id).resolve()
        target = (base / relative).resolve()
        if base != target and base not in target.parents:
            raise ValueError("Invalid media path")
        return target

    def write_json(self, project_id: str, relative: str, payload: object) -> Path:
        path = self.media_path(project_id, relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def read_json(self, project_id: str, relative: str, default=None):
        path = self.media_path(project_id, relative)
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
