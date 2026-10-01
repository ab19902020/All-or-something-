from __future__ import annotations

from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import tempfile

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .core.jobs import JobManager
from .core.local_ai import describe_style, ollama_available
from .core.local_image import comfy_available, generate as generate_local_image
from .core.pipeline import PipelineError, StudioPipeline
from .core.storage import ASSET_KINDS, ProjectStore


STUDIO_ROOT = Path(__file__).resolve().parent
WEB_ROOT = STUDIO_ROOT / "web"
store = ProjectStore()
pipeline = StudioPipeline(store, STUDIO_ROOT)
jobs = JobManager(workers=int(os.environ.get("URS_WORKERS", "2")))

app = FastAPI(title="United Road Studio", version="0.2.0")
allowed_origins = ["null"]
allowed_origins.extend(
    origin.strip()
    for origin in os.environ.get("URS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=WEB_ROOT), name="static")


def project_payload(project_id: str) -> dict:
    try:
        project = store.load(project_id)
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")
    return {
        "id": project_id,
        **asdict(project),
        "settings": store.read_settings(project_id),
        "plan": store.read_json(project_id, "plans/scene_plan.json", None),
        "qa": store.read_json(project_id, "qa/latest.json", None),
        "has_preview": (store.project_dir(project_id) / "renders" / "preview.mp4").exists(),
        "has_master": (store.project_dir(project_id) / "renders" / "master_4k.mp4").exists(),
    }


@app.get("/")
def home():
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/app.js")
def web_app_js():
    return FileResponse(WEB_ROOT / "app.js", media_type="application/javascript")


@app.get("/styles.css")
def web_styles():
    return FileResponse(WEB_ROOT / "styles.css", media_type="text/css")


@app.get("/manifest.webmanifest")
def web_manifest():
    return FileResponse(WEB_ROOT / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(
        WEB_ROOT / "sw.js",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.get("/icon.svg")
def web_icon():
    return FileResponse(WEB_ROOT / "icon.svg", media_type="image/svg+xml")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "name": "United Road Studio Engine",
        "version": "0.2.0",
        "mobile_ready": True,
        "workspace": str(store.root),
    }


@app.get("/api/projects")
def list_projects():
    return store.list()


@app.post("/api/projects")
def create_project(payload: dict = Body(...)):
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(400, "Title is required")
    project_id, _ = store.create(title)
    return project_payload(project_id)


@app.get("/api/projects/{project_id}")
def get_project(project_id: str):
    return project_payload(project_id)


@app.patch("/api/projects/{project_id}")
def update_project(project_id: str, payload: dict = Body(...)):
    try:
        project = store.load(project_id)
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")
    for key in ("title", "director_notes", "production_notes"):
        if key in payload:
            setattr(project, key, str(payload[key]))
    project.mark_draft()
    store.invalidate(project_id, plan=True, transcripts=False)
    store.save(project_id, project)
    return project_payload(project_id)


@app.patch("/api/projects/{project_id}/settings")
def update_settings(project_id: str, payload: dict = Body(...)):
    try:
        store.load(project_id)
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")
    allowed = {
        "director_mode", "ollama_url", "director_model", "vision_model", "whisper_model",
        "renderer", "legacy_root", "legacy_scene", "comfyui_url", "comfy_checkpoint",
    }
    current = store.read_settings(project_id)
    for key, value in payload.items():
        if key in allowed:
            current[key] = value
    store.write_settings(project_id, current)
    project = store.load(project_id)
    project.mark_draft()
    store.invalidate(project_id, plan=True, transcripts=False)
    store.save(project_id, project)
    return current


@app.post("/api/projects/{project_id}/upload/{kind}")
async def upload_assets(project_id: str, kind: str, files: list[UploadFile] = File(...)):
    if kind not in ASSET_KINDS:
        raise HTTPException(400, "Unsupported upload type")
    try:
        store.load(project_id)
    except FileNotFoundError:
        raise HTTPException(404, "Project not found")

    uploaded = []
    for item in files:
        suffix = Path(item.filename or "").suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while chunk := await item.read(1024 * 1024):
                tmp.write(chunk)
            tmp_path = Path(tmp.name)
        try:
            uploaded.append(store.add_asset(project_id, kind, tmp_path, item.filename or "asset"))
        finally:
            tmp_path.unlink(missing_ok=True)
    return {"uploaded": uploaded, "project": project_payload(project_id)}


@app.get("/api/projects/{project_id}/media/{relative:path}")
def media(project_id: str, relative: str):
    try:
        path = store.media_path(project_id, relative)
    except ValueError:
        raise HTTPException(400, "Invalid path")
    if not path.exists() or not path.is_file():
        raise HTTPException(404, "Media not found")
    return FileResponse(path)


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job.public()


@app.get("/api/projects/{project_id}/jobs")
def project_jobs(project_id: str):
    return jobs.recent(project_id)


def submit(kind: str, project_id: str, fn):
    job = jobs.submit(kind, project_id, fn)
    return {"job_id": job.id, "status": job.status}


@app.post("/api/projects/{project_id}/transcribe")
def transcribe(project_id: str):
    store.load(project_id)
    return submit("transcribe", project_id, lambda: pipeline.transcribe(project_id))


@app.post("/api/projects/{project_id}/plan")
def plan(project_id: str):
    store.load(project_id)
    return submit("plan", project_id, lambda: pipeline.plan(project_id))


@app.post("/api/projects/{project_id}/render/{profile}")
def render(project_id: str, profile: str):
    store.load(project_id)
    if profile not in pipeline.policy.profiles:
        raise HTTPException(400, "Unknown render profile")

    def task():
        result = pipeline.render_review_loop(project_id, profile)
        path = result["path"]
        return {
            "media": str(path.relative_to(store.project_dir(project_id))),
            "qa": result.get("qa"),
            "repair_attempts": result.get("repair_attempts", 0),
        }
    return submit("render", project_id, task)


@app.post("/api/projects/{project_id}/review")
def review(project_id: str):
    store.load(project_id)
    return submit("review", project_id, lambda: pipeline.review(project_id))


@app.post("/api/projects/{project_id}/approve")
def approve(project_id: str):
    project = store.load(project_id)
    qa = store.read_json(project_id, "qa/latest.json", None)
    if not qa or not qa.get("passed"):
        raise HTTPException(409, "The latest preview must pass self-review before final approval.")
    project.approve_final_master()
    store.save(project_id, project)
    return project_payload(project_id)


@app.get("/api/projects/{project_id}/services")
def services(project_id: str):
    settings = store.read_settings(project_id)
    ollama_url = settings.get("ollama_url", "http://127.0.0.1:11434")
    comfy_url = settings.get("comfyui_url", "http://127.0.0.1:8188")
    return {
        "ollama": ollama_available(ollama_url),
        "comfyui": comfy_available(comfy_url),
        "renderer": settings.get("renderer", "auto"),
    }


@app.post("/api/projects/{project_id}/generate-image")
def generate_image(project_id: str, payload: dict = Body(...)):
    project = store.load(project_id)
    settings = store.read_settings(project_id)
    prompt = str(payload.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(400, "Prompt is required")

    # Style references are deliberately not sent as composition references here.
    # A local vision model can be used by the director/QA stages to keep style consistent.
    style_text = str(payload.get("style_description") or "").strip()

    def task():
        effective_style = style_text
        if not effective_style and project.style_references:
            effective_style = describe_style(
                [store.media_path(project_id, p) for p in project.style_references],
                settings.get("ollama_url", "http://127.0.0.1:11434"),
                settings.get("vision_model", "qwen2.5vl:7b"),
            )
        dest = generate_local_image(
            store.project_dir(project_id) / "generated",
            settings.get("comfyui_url", "http://127.0.0.1:8188"),
            settings.get("comfy_checkpoint", ""),
            prompt,
            style_description=effective_style,
            negative=str(payload.get("negative") or "photorealistic, 3d render, malformed face, extra limbs, text, watermark"),
            width=int(payload.get("width") or 1024),
            height=int(payload.get("height") or 576),
            seed=int(payload.get("seed") or 1),
        )
        return {"media": str(dest.relative_to(store.project_dir(project_id)))}

    return submit("generate-image", project_id, task)
