from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict
from pathlib import Path

import cv2
import numpy as np

from .local_ai import local_director_plan, local_repair_plan, local_visual_review, ollama_available, transcribe_file
from .project import EpisodeProject
from .render_policy import RenderPolicy, RenderRequest
from .self_review import SelfReview
from .storage import ProjectStore


class PipelineError(RuntimeError):
    pass


class StudioPipeline:
    def __init__(self, store: ProjectStore, studio_root: Path):
        self.store = store
        self.studio_root = studio_root
        self.policy = RenderPolicy(studio_root / "config" / "render_profiles.json")

    def transcribe(self, project_id: str) -> list[dict]:
        settings = self.store.read_settings(project_id)
        model = settings.get("whisper_model", "small.en")
        project = self.store.load(project_id)
        out = []
        for rel in project.voiceovers:
            audio = self.store.media_path(project_id, rel)
            cache = self.store.project_dir(project_id) / "transcripts" / (audio.stem + ".json")
            if cache.exists() and cache.stat().st_mtime >= audio.stat().st_mtime:
                transcript = json.loads(cache.read_text(encoding="utf-8"))
            else:
                transcript = transcribe_file(audio, model)
                cache.write_text(json.dumps(transcript, indent=2), encoding="utf-8")
            out.append({"clip": rel, "transcript": transcript})
        self.store.write_json(project_id, "transcripts/all.json", out)
        return out

    def plan(self, project_id: str) -> dict:
        project = self.store.load(project_id)
        transcripts = self.store.read_json(project_id, "transcripts/all.json", [])
        if not transcripts and project.voiceovers:
            transcripts = self.transcribe(project_id)
        settings = self.store.read_settings(project_id)
        plan = local_director_plan(
            asdict(project),
            transcripts,
            settings.get("ollama_url", "http://127.0.0.1:11434"),
            settings.get("director_model", "qwen2.5:7b"),
        )
        self.store.write_json(project_id, "plans/scene_plan.json", plan)
        return plan

    @staticmethod
    def _duration(path: Path) -> float:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ]
        try:
            return max(float(subprocess.check_output(cmd, text=True).strip()), 0.1)
        except Exception:
            return 3.0

    @staticmethod
    def _audio_envelope(path: Path, fps: int) -> np.ndarray:
        """Speech-energy envelope used for subtle speech-synced motion."""
        try:
            raw = subprocess.check_output([
                "ffmpeg", "-v", "error", "-i", str(path),
                "-f", "s16le", "-ac", "1", "-ar", "8000", "-"
            ])
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            hop = max(1, int(8000 / max(fps, 1)))
            n = max(1, math.ceil(len(samples) / hop))
            env = np.zeros(n, np.float32)
            for i in range(n):
                seg = samples[i * hop:(i + 1) * hop]
                if len(seg):
                    env[i] = float(np.sqrt(np.mean(seg * seg)))
            peak = float(np.percentile(env, 95)) if len(env) else 0.0
            if peak > 1e-6:
                env = np.clip(env / peak, 0.0, 1.0)
            return env
        except Exception:
            return np.zeros(max(1, int(3 * fps)), np.float32)

    @staticmethod
    def _fit_cover(img: np.ndarray, width: int, height: int) -> np.ndarray:
        h, w = img.shape[:2]
        scale = max(width / max(w, 1), height / max(h, 1))
        nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
        resized = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
        x = max(0, (nw - width) // 2)
        y = max(0, (nh - height) // 2)
        return resized[y:y + height, x:x + width].copy()

    @staticmethod
    def _read_rgba(path: Path) -> np.ndarray | None:
        img = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if img is None:
            return None
        if img.ndim == 2:
            return cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
        if img.shape[2] == 3:
            alpha = np.full(img.shape[:2] + (1,), 255, np.uint8)
            return np.concatenate([img, alpha], axis=2)
        return img

    @staticmethod
    def _over(frame: np.ndarray, rgba: np.ndarray, x: int, y: int) -> None:
        h, w = rgba.shape[:2]
        H, W = frame.shape[:2]
        xa, ya, xb, yb = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
        if xa >= xb or ya >= yb:
            return
        src = rgba[ya-y:yb-y, xa-x:xb-x].astype(np.float32)
        alpha = src[..., 3:4] / 255.0
        dst = frame[ya:yb, xa:xb].astype(np.float32)
        frame[ya:yb, xa:xb] = (src[..., :3] * alpha + dst * (1 - alpha)).clip(0,255).astype(np.uint8)

    def _generic_preview(self, project_id: str, profile_name: str) -> Path:
        project = self.store.load(project_id)
        profile = self.policy.resolve(RenderRequest(profile_name, project.final_master_approved))
        W, H, fps = int(profile["width"]), int(profile["height"]), int(profile["fps"])
        pdir = self.store.project_dir(project_id)
        backgrounds = [self.store.media_path(project_id, p) for p in project.background_assets]
        characters = [self.store.media_path(project_id, p) for p in project.character_assets]
        audios = [self.store.media_path(project_id, p) for p in project.voiceovers]
        if not audios:
            raise PipelineError("Upload at least one voiceover before rendering.")

        durations = [self._duration(p) for p in audios]
        envelopes = [self._audio_envelope(p, fps) for p in audios]
        total = sum(durations)
        plan = self.store.read_json(project_id, "plans/scene_plan.json", {}) or {}
        plan_scenes = plan.get("scenes", [])

        audio_list = pdir / "renders" / "_audio_concat.txt"
        with audio_list.open("w", encoding="utf-8") as fh:
            for a in audios:
                escaped = str(a).replace("'", "'\\''")
                fh.write(f"file '{escaped}'\n")
        mixed_audio = pdir / "renders" / "_voice_track.m4a"
        subprocess.run([
            "ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(audio_list),
            "-c:a","aac","-b:a",profile.get("audio_bitrate","192k"),str(mixed_audio)
        ], check=True)

        out_name = "master_4k.mp4" if profile_name == "final_master_4k" else "preview.mp4"
        output = pdir / "renders" / out_name
        cmd = [
            "ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24",
            "-s",f"{W}x{H}","-r",str(fps),"-i","-","-i",str(mixed_audio),
            "-c:v","libx264","-preset",profile["preset"],"-crf",str(profile["crf"]),
            "-pix_fmt","yuv420p","-c:a","aac","-b:a",profile.get("audio_bitrate","192k"),
            "-shortest","-movflags","+faststart",str(output)
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        bg_cache = []
        for p in backgrounds:
            img = cv2.imread(str(p))
            if img is not None:
                bg_cache.append(self._fit_cover(img, W, H))
        char_cache = [x for x in (self._read_rgba(p) for p in characters) if x is not None]

        clip_starts = []
        t = 0.0
        for d in durations:
            clip_starts.append(t)
            t += d

        frames = max(1, math.ceil(total * fps))
        for f in range(frames):
            t = f / fps
            ci = 0
            for i, st in enumerate(clip_starts):
                if t >= st:
                    ci = i
            local_t = max(0.0, t - clip_starts[ci])
            duration = durations[ci]
            scene = plan_scenes[ci] if ci < len(plan_scenes) else {}
            shot = str(scene.get("shot", "medium")).lower()
            energy = str(scene.get("energy", "medium")).lower()
            camera = str(scene.get("camera", "gentle push")).lower()
            if bg_cache:
                frame = bg_cache[ci % len(bg_cache)].copy()
            else:
                frame = np.full((H, W, 3), (28, 28, 32), np.uint8)

            # restrained camera direction from the generated scene plan
            push_amount = 0.0 if "locked" in camera else (0.04 if shot == "close" else 0.025)
            push = 1.0 + push_amount * min(local_t / max(duration, 0.1), 1.0)
            if push > 1.001:
                crop_w, crop_h = int(W / push), int(H / push)
                x0, y0 = (W - crop_w)//2, (H - crop_h)//2
                frame = cv2.resize(frame[y0:y0+crop_h, x0:x0+crop_w], (W,H), interpolation=cv2.INTER_LINEAR)

            if char_cache:
                # Hold poses long enough to read; cycle uploaded poses on dialogue phrases.
                phrase = int(local_t / (1.8 if energy == "low" else 1.35))
                rgba = char_cache[(ci + phrase) % len(char_cache)]
                target_fraction = {"wide": 0.62, "medium": 0.78, "close": 1.02}.get(shot, 0.78)
                target_h = int(H * target_fraction)
                base_scale = target_h / max(rgba.shape[0], 1)
                env = envelopes[ci]
                local_frame = min(len(env) - 1, max(0, int(local_t * fps)))
                speech = float(env[local_frame]) if len(env) else 0.0
                motion = {"low": 0.9, "medium": 2.2, "high": 4.4}.get(energy, 2.2)
                bob = int(math.sin(t * 6.8) * motion + speech * motion * -1.6)
                scale = base_scale * (1.0 + speech * 0.012)
                rw = max(1, int(rgba.shape[1] * scale))
                rh = max(1, int(rgba.shape[0] * scale))
                actor = cv2.resize(rgba, (rw, rh), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
                x_shift = int(math.sin(t * 0.65) * (6 if shot != "close" else 3))
                self._over(frame, actor, (W-rw)//2 + x_shift, H-rh-12+bob)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        code = proc.wait()
        if code != 0 or not output.exists():
            raise PipelineError("Preview render failed.")
        return output

    def _legacy_render(self, project_id: str, profile_name: str, settings: dict) -> Path:
        project = self.store.load(project_id)
        profile = self.policy.resolve(RenderRequest(profile_name, project.final_master_approved))
        root = Path(settings.get("legacy_root", "")).expanduser()
        scene = settings.get("legacy_scene", "")
        if not root.exists():
            raise PipelineError("Legacy renderer root does not exist.")
        if not scene:
            raise PipelineError("Choose a legacy scene file first.")

        scene_path = (root / scene).resolve()
        if root.resolve() not in scene_path.parents:
            raise PipelineError("Legacy scene must be inside the selected legacy repository.")

        if (root / "tools" / "render_episode.py").exists() and scene_path.suffix == ".py":
            quality = "4k" if profile_name == "final_master_4k" else "720p"
            cmd = ["python3", str(root / "tools" / "render_episode.py"), str(scene_path), quality]
        elif (root / "tools" / "render_scene.py").exists() and scene_path.suffix == ".json":
            cmd = ["python3", str(root / "tools" / "render_scene.py"), str(scene_path)]
        else:
            raise PipelineError("No supported legacy renderer was found.")

        env = os.environ.copy()
        env.update({
            "URS_PROFILE": profile_name,
            "URS_WIDTH": str(profile["width"]),
            "URS_HEIGHT": str(profile["height"]),
            "URS_FPS": str(profile["fps"]),
        })
        subprocess.run(cmd, cwd=root, env=env, check=True)
        candidates = sorted((root / "out").glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not candidates:
            raise PipelineError("Legacy renderer completed but no MP4 was found.")
        dest = self.store.project_dir(project_id) / "renders" / (
            "master_4k.mp4" if profile_name == "final_master_4k" else "preview.mp4"
        )
        shutil.copy2(candidates[0], dest)
        return dest

    def render(self, project_id: str, profile_name: str = "preview_review") -> Path:
        project = self.store.load(project_id)
        if project.voiceovers and not self.store.read_json(project_id, "plans/scene_plan.json", None):
            # One-button workflow: transcription + direction happen automatically when needed.
            self.plan(project_id)
        settings = self.store.read_settings(project_id)
        renderer = settings.get("renderer", "auto")
        if renderer == "legacy" or (renderer == "auto" and settings.get("legacy_root") and settings.get("legacy_scene")):
            return self._legacy_render(project_id, profile_name, settings)
        return self._generic_preview(project_id, profile_name)

    def render_review_loop(self, project_id: str, profile_name: str = "preview_review", max_repairs: int = 2) -> dict:
        """Render, inspect, and locally repair direction before handing the preview to the director."""
        path = self.render(project_id, profile_name)
        if profile_name == "final_master_4k":
            return {"path": path, "qa": None, "repair_attempts": 0}

        report = self.review(project_id)
        attempts = 0
        settings = self.store.read_settings(project_id)
        renderer = settings.get("renderer", "auto")
        using_generic = renderer == "generic" or (
            renderer == "auto" and not (settings.get("legacy_root") and settings.get("legacy_scene"))
        )
        base_url = settings.get("ollama_url", "http://127.0.0.1:11434")
        model = settings.get("director_model", "qwen2.5:7b")

        while (
            not report.get("passed")
            and using_generic
            and attempts < max_repairs
            and ollama_available(base_url)
        ):
            current = self.store.read_json(project_id, "plans/scene_plan.json", {}) or {}
            revised = local_repair_plan(current, report, base_url, model)
            if revised == current:
                break
            attempts += 1
            self.store.write_json(project_id, "plans/scene_plan.json", revised)
            path = self._generic_preview(project_id, profile_name)
            report = self.review(project_id)

        return {"path": path, "qa": report, "repair_attempts": attempts}

    def review(self, project_id: str) -> dict:
        pdir = self.store.project_dir(project_id)
        preview = pdir / "renders" / "preview.mp4"
        if not preview.exists():
            raise PipelineError("Render a preview before self-review.")

        deterministic = SelfReview().review_video(preview, sample_every=2)
        sample_dir = pdir / "qa" / "frames"
        sample_dir.mkdir(parents=True, exist_ok=True)
        for old in sample_dir.glob("*.jpg"):
            old.unlink()

        cap = cv2.VideoCapture(str(preview))
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(cap.get(cv2.CAP_PROP_FPS) or 30)
        every = max(1, int(max(count, 1) / 10))
        sample_paths = []
        i = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if i % every == 0 and len(sample_paths) < 10:
                path = sample_dir / f"frame_{i:06d}.jpg"
                cv2.imwrite(str(path), frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                sample_paths.append(path)
            i += 1
        cap.release()

        project = self.store.load(project_id)
        settings = self.store.read_settings(project_id)
        visual = local_visual_review(
            sample_paths,
            [self.store.media_path(project_id, p) for p in project.style_references],
            asdict(project),
            settings.get("ollama_url", "http://127.0.0.1:11434"),
            settings.get("vision_model", "qwen2.5vl:7b"),
        )
        findings = [
            {"severity": f.severity, "category": f.code, "message": f.message, "frame_index": f.frame}
            for f in deterministic.findings
        ]
        if visual:
            findings.extend(visual.get("findings", []))

        passed = not any(f.get("severity") == "block" for f in findings)
        report = {
            "passed": passed,
            "deterministic_passed": deterministic.passed,
            "vision_review_used": visual is not None,
            "findings": findings,
            "summary": (visual or {}).get("summary") or (
                "Automated checks passed." if passed else "Automated checks found blocking issues."
            ),
        }
        self.store.write_json(project_id, "qa/latest.json", report)
        if passed:
            project.mark_review()
        else:
            project.mark_draft()
        self.store.save(project_id, project)
        return report
