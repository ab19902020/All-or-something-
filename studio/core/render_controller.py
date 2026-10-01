from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .project import EpisodeProject
from .render_policy import RenderPolicy, RenderRequest


@dataclass(frozen=True)
class RenderJob:
    input_path: Path
    output_path: Path
    profile: str


class RenderController:
    def __init__(self, policy: RenderPolicy):
        self.policy = policy

    def profile_for(self, project: EpisodeProject, profile_name: str) -> dict:
        return self.policy.resolve(
            RenderRequest(
                profile=profile_name,
                final_master_approved=project.final_master_approved,
            )
        )

    def ffmpeg_encode_command(
        self,
        project: EpisodeProject,
        raw_video: str,
        audio_file: str,
        output_file: str,
        profile_name: str,
    ) -> list[str]:
        p = self.profile_for(project, profile_name)
        fps = str(p["fps"])
        size = f'{p["width"]}x{p["height"]}'
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", size, "-r", fps, "-i", raw_video,
            "-i", audio_file,
            "-c:v", "libx264",
            "-preset", p["preset"],
            "-crf", str(p["crf"]),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", p.get("audio_bitrate", "192k"),
            "-shortest", "-movflags", "+faststart",
            output_file,
        ]
        return cmd

    def run_existing_render_command(
        self,
        project: EpisodeProject,
        command: Iterable[str],
        profile_name: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        profile = self.profile_for(project, profile_name)
        merged_env = os.environ.copy()\n        merged_env.update(env or {})
        merged_env.update({
            "URS_PROFILE": profile_name,
            "URS_WIDTH": str(profile["width"]),
            "URS_HEIGHT": str(profile["height"]),
            "URS_FPS": str(profile["fps"]),
            "URS_CRF": str(profile["crf"]),
            "URS_PRESET": str(profile["preset"]),
        })
        return subprocess.run(list(command), check=True, env=merged_env)
