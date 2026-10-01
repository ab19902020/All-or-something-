from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderRequest:
    profile: str
    final_master_approved: bool = False


class RenderPolicyError(RuntimeError):
    pass


class RenderPolicy:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.profiles = json.loads(self.config_path.read_text(encoding="utf-8"))

    def resolve(self, request: RenderRequest) -> dict:
        if request.profile not in self.profiles:
            raise RenderPolicyError(f"Unknown render profile: {request.profile}")

        profile = dict(self.profiles[request.profile])
        if profile.get("requires_approval") and not request.final_master_approved:
            raise RenderPolicyError(
                "Final 4K master is locked until the director marks the episode approved."
            )
        return profile

    def available_profiles(self, final_master_approved: bool = False) -> dict:
        result = {}
        for key, profile in self.profiles.items():
            if profile.get("requires_approval") and not final_master_approved:
                continue
            result[key] = dict(profile)
        return result
