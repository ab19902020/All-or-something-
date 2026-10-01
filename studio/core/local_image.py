from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path


class LocalImageError(RuntimeError):
    pass


def _json_request(url: str, payload: dict | None = None, timeout: int = 30) -> dict:
    if payload is None:
        req = urllib.request.Request(url)
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def comfy_available(base_url: str) -> bool:
    try:
        _json_request(base_url.rstrip("/") + "/system_stats", timeout=2)
        return True
    except Exception:
        return False


def basic_workflow(
    checkpoint: str,
    positive: str,
    negative: str,
    width: int = 1024,
    height: int = 576,
    steps: int = 28,
    cfg: float = 6.5,
    seed: int = 1,
) -> dict:
    """Portable ComfyUI txt2img workflow using only core nodes."""
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": int(seed),
                "steps": int(steps),
                "cfg": float(cfg),
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": checkpoint}},
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"width": int(width), "height": int(height), "batch_size": 1},
        },
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "UnitedRoadStudio", "images": ["8", 0]},
        },
    }


def generate(
    output_dir: Path,
    base_url: str,
    checkpoint: str,
    prompt: str,
    style_description: str = "",
    negative: str = "photorealistic, 3d render, malformed face, extra limbs, text, watermark",
    width: int = 1024,
    height: int = 576,
    seed: int = 1,
    timeout: int = 300,
) -> Path:
    if not checkpoint:
        raise LocalImageError("Set a local ComfyUI checkpoint name in Studio settings.")
    if not comfy_available(base_url):
        raise LocalImageError("Local ComfyUI is not reachable.")

    positive = prompt.strip()
    if style_description.strip():
        positive += "\nSTYLE ONLY: " + style_description.strip()

    workflow = basic_workflow(checkpoint, positive, negative, width, height, seed=seed)
    queued = _json_request(base_url.rstrip("/") + "/prompt", {"prompt": workflow}, timeout=30)
    prompt_id = queued.get("prompt_id")
    if not prompt_id:
        raise LocalImageError(f"ComfyUI did not return a prompt id: {queued}")

    deadline = time.time() + timeout
    item = None
    while time.time() < deadline:
        history = _json_request(base_url.rstrip("/") + f"/history/{prompt_id}", timeout=10)
        item = history.get(prompt_id)
        if item and item.get("outputs"):
            break
        time.sleep(1.0)
    if not item:
        raise LocalImageError("ComfyUI generation timed out.")

    images = []
    for output in item.get("outputs", {}).values():
        images.extend(output.get("images", []))
    if not images:
        raise LocalImageError("ComfyUI finished without an output image.")

    image = images[0]
    params = urllib.parse.urlencode({
        "filename": image["filename"],
        "subfolder": image.get("subfolder", ""),
        "type": image.get("type", "output"),
    })
    with urllib.request.urlopen(base_url.rstrip("/") + "/view?" + params, timeout=30) as response:
        data = response.read()

    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / f"generated_{int(time.time())}.png"
    dest.write_bytes(data)
    return dest
