from __future__ import annotations

import base64
import json
import mimetypes
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


def _post_json(url: str, payload: dict, timeout: int = 120) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def ollama_available(base_url: str = "http://127.0.0.1:11434") -> bool:
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/api/tags", timeout=2) as response:
            return response.status == 200
    except Exception:
        return False


def transcribe_file(path: str | Path, model_name: str = "small.en") -> dict:
    """Transcribe locally with faster-whisper. No cloud call is made."""
    path = Path(path)
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise RuntimeError(
            "Local transcription needs faster-whisper. Run: pip install -r studio/requirements.txt"
        ) from exc

    device = os.environ.get("URS_WHISPER_DEVICE", "auto")
    compute = os.environ.get("URS_WHISPER_COMPUTE", "int8")
    model = WhisperModel(model_name, device=device, compute_type=compute)
    segments, info = model.transcribe(
        str(path),
        word_timestamps=True,
        vad_filter=True,
        beam_size=5,
    )
    out_segments = []
    words = []
    for seg in segments:
        item = {
            "start": float(seg.start),
            "end": float(seg.end),
            "text": seg.text.strip(),
            "words": [],
        }
        for word in seg.words or []:
            w = {
                "start": float(word.start),
                "end": float(word.end),
                "word": word.word.strip(),
                "probability": float(word.probability),
            }
            item["words"].append(w)
            words.append(w)
        out_segments.append(item)
    return {
        "language": info.language,
        "language_probability": float(info.language_probability),
        "duration": float(info.duration),
        "segments": out_segments,
        "words": words,
        "text": " ".join(s["text"] for s in out_segments).strip(),
    }


def rule_based_plan(project: dict, transcripts: list[dict]) -> dict:
    """Useful offline fallback when no local LLM is running."""
    lines = []
    for index, item in enumerate(transcripts):
        transcript = item.get("transcript", {})
        duration = float(transcript.get("duration") or 0)
        text = transcript.get("text", "")
        lower = text.lower()
        if any(k in lower for k in ("shout", "angry", "furious", "unbelievable")):
            shot = "close"
            energy = "high"
        elif any(k in lower for k in ("look", "there", "this", "that", "watch")):
            shot = "medium"
            energy = "medium"
        else:
            shot = "medium" if index % 3 else "wide"
            energy = "medium"
        lines.append({
            "clip": item.get("clip"),
            "order": index,
            "duration": duration,
            "text": text,
            "shot": shot,
            "camera": "gentle push" if shot != "wide" else "locked wide",
            "energy": energy,
            "character_action": "natural talking gesture",
            "cut_reason": "dialogue phrase",
        })

    return {
        "version": 1,
        "source": "offline-rules",
        "title": project.get("title", "Untitled"),
        "director_notes": project.get("director_notes", ""),
        "production_notes": project.get("production_notes", ""),
        "style_rule": "Style references control visual language only; do not copy their composition or identity.",
        "scenes": lines,
        "quality_rules": [
            "Keep mouth movement synchronized to speech.",
            "Avoid floating props or detached body parts.",
            "Keep faces and character proportions consistent with character assets.",
            "Use deliberate camera cuts; avoid random movement.",
            "Maintain readable silhouettes and clean alpha edges.",
        ],
    }


def local_director_plan(
    project: dict,
    transcripts: list[dict],
    base_url: str,
    model: str,
) -> dict:
    if not ollama_available(base_url):
        return rule_based_plan(project, transcripts)

    compact = [
        {
            "clip": x.get("clip"),
            "duration": x.get("transcript", {}).get("duration"),
            "text": x.get("transcript", {}).get("text"),
        }
        for x in transcripts
    ]
    prompt = f"""You are the director inside United Road Studio, a local 2.5D cut-out animation pipeline.
Return ONLY valid JSON. Create a precise scene plan from the voice clips and notes.

Hard rules:
- Preserve uploaded character identity and supplied art style.
- Style reference images are STYLE ONLY, never composition or identity templates.
- Favor purposeful cuts, reactions, eyelines, blinks, gestures and camera movement.
- Mouths must use proper visemes/phonemes, close between speech, and never float.
- Props must remain attached to hands.
- No unrequested text overlays.
- Keep animation visually coherent and feasible for a Python/OpenCV/vector cut-out renderer.
- Include scenes[] with clip, order, duration, text, shot, camera, energy, character_action, cut_reason.
- Include quality_rules[].

Project:
{json.dumps(project, indent=2)}

Transcripts:
{json.dumps(compact, indent=2)}
"""
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0.35},
    }
    try:
        response = _post_json(base_url.rstrip("/") + "/api/chat", payload, timeout=180)
        content = response.get("message", {}).get("content", "{}")
        return json.loads(content)
    except Exception:
        return rule_based_plan(project, transcripts)


def _encode_image(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def local_visual_review(
    frame_paths: Iterable[Path],
    style_refs: Iterable[Path],
    brief: dict,
    base_url: str,
    model: str,
) -> dict | None:
    """Ask a local vision model to inspect the preview. Returns None if unavailable."""
    if not ollama_available(base_url):
        return None

    frames = list(frame_paths)
    refs = list(style_refs)
    images = [_encode_image(p) for p in refs[:4] + frames[:12] if p.exists()]
    prompt = f"""You are the visual QA supervisor for a 2.5D cartoon animation studio.
The FIRST {min(len(refs),4)} images are STYLE-ONLY references. Do not require the shot composition to match them.
The remaining images are ordered frames sampled from the latest preview.

Inspect for objective animation defects: face/head misalignment, mouths detached or wrong size, eyes/blinks broken,
floating microphones/props, limbs detached, bad cut-out edges, wrong layering, character inconsistency, accidental
style drift, strange scaling, clipping, black/blank frames, camera framing failures, and obvious continuity errors.

Return ONLY JSON with:
{{"passed": boolean, "findings":[{{"severity":"block|warn","category":"...","message":"...","frame_index":number|null}}], "summary":"..."}}

Project brief:
{json.dumps(brief, indent=2)}
"""
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [{"role": "user", "content": prompt, "images": images}],
        "options": {"temperature": 0.1},
    }
    try:
        response = _post_json(base_url.rstrip("/") + "/api/chat", payload, timeout=240)
        return json.loads(response.get("message", {}).get("content", "{}"))
    except Exception:
        return None


def describe_style(
    style_refs: Iterable[Path],
    base_url: str,
    model: str,
) -> str:
    """Create a style-only description locally from reference images."""
    refs = [p for p in style_refs if p.exists()][:6]
    if not refs or not ollama_available(base_url):
        return ""
    images = [_encode_image(p) for p in refs]
    prompt = """These images are STYLE REFERENCES ONLY for an animation studio.
Describe only the reusable visual language: line weight, outline character, shape design, palette behavior,
shading, texture, proportions, background treatment, lighting, and compositing feel.
Do NOT describe identities, poses, exact objects, scene layout, framing, or composition.
Return one concise paragraph suitable as a generation style prompt."""
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": prompt, "images": images}],
        "options": {"temperature": 0.1},
    }
    try:
        response = _post_json(base_url.rstrip("/") + "/api/chat", payload, timeout=180)
        return response.get("message", {}).get("content", "").strip()
    except Exception:
        return ""


def local_repair_plan(
    plan: dict,
    qa_report: dict,
    base_url: str,
    model: str,
) -> dict:
    """Revise a scene plan locally using visual-QA findings."""
    if not ollama_available(base_url):
        return plan
    prompt = f"""You are repairing a 2.5D cut-out animation direction plan after visual QA.
Return ONLY the full revised plan as valid JSON.

You may change shot size, camera movement, energy, pose/character_action timing and cut reasons.
Do not change dialogue text or clip order. Do not invent new characters. Keep style references style-only.
Specifically address every blocking QA finding where a direction/timing change can help.

CURRENT PLAN:
{json.dumps(plan, indent=2)}

QA REPORT:
{json.dumps(qa_report, indent=2)}
"""
    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "messages": [{"role": "user", "content": prompt}],
        "options": {"temperature": 0.2},
    }
    try:
        response = _post_json(base_url.rstrip("/") + "/api/chat", payload, timeout=180)
        revised = json.loads(response.get("message", {}).get("content", "{}"))
        return revised if revised.get("scenes") else plan
    except Exception:
        return plan
