"""Chat UI server — FastAPI + agent loop."""

from __future__ import annotations

import json
import subprocess
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from hermes_app.agent.loop import AgentLoop

PROJECT_ROOT = Path(__file__).resolve().parents[3]
STATIC_DIR = PROJECT_ROOT / "web" / "static"
LEAD_DEMO_SKILL_DIR = (
    PROJECT_ROOT / "templates" / "sales-lead-pipeline" / "skills" / "lead-demo-site"
)
app = FastAPI(title="Hermes Agent App", version="0.3.0")
agent = AgentLoop()

HERMES_HOME = Path.home() / ".hermes"
LEADS_DIR = HERMES_HOME / "leads"
RESEARCH_DIR = LEADS_DIR / "research"
DEMOS_DIR = LEADS_DIR / "demos"

RUNS: dict[str, dict] = {}


def _safe_read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _iso_mtime(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).isoformat()
    except Exception:
        return ""


def _list_research() -> list[dict]:
    if not RESEARCH_DIR.exists():
        return []
    items: list[dict] = []
    for p in sorted(RESEARCH_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
        data = _safe_read_json(p)
        meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
        slug = (meta.get("slug") or p.stem) if isinstance(meta, dict) else p.stem
        items.append(
            {
                "slug": slug,
                "path": str(p),
                "updated_at": _iso_mtime(p),
                "business": meta.get("business") if isinstance(meta, dict) else None,
                "city": meta.get("city") if isinstance(meta, dict) else None,
                "category": meta.get("category") if isinstance(meta, dict) else None,
            }
        )
    return items


def _list_demos() -> list[dict]:
    if not DEMOS_DIR.exists():
        return []
    items: list[dict] = []
    for d in sorted([p for p in DEMOS_DIR.iterdir() if p.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True):
        meta = _safe_read_json(d / "meta.json")
        slug = (meta.get("slug") or d.name) if isinstance(meta, dict) else d.name
        demo_index = d / "index.html"
        items.append(
            {
                "slug": slug,
                "path": str(demo_index if demo_index.exists() else d),
                "updated_at": _iso_mtime(d),
                "template_used": meta.get("template_used") if isinstance(meta, dict) else None,
                "demo_url": meta.get("demo_url") if isinstance(meta, dict) else None,
            }
        )
    return items


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    report_updated: bool
    tools_used: list[str]


class LeadFinderRequest(BaseModel):
    city: str = ""
    category: str = ""


class RunStartRequest(BaseModel):
    kind: str
    city: str = ""
    category: str = ""
    business: str = ""
    slug: str = ""
    template: str = ""
    limit: int = 10


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/app")
@app.get("/app/")
def app_ui() -> FileResponse:
    return FileResponse(STATIC_DIR / "app" / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    try:
        result = agent.chat(req.message.strip(), session_id=req.session_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return ChatResponse(**result)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/pipeline/state")
def pipeline_state() -> dict:
    research = _list_research()
    demos = _list_demos()
    return {
        "ok": True,
        "counts": {"research": len(research), "demos": len(demos)},
        "research": research,
        "demos": demos,
    }


@app.post("/api/pipeline/lead-finder")
def pipeline_lead_finder(req: LeadFinderRequest) -> dict:
    city = (req.city or "").strip()
    category = (req.category or "").strip()

    if not city or not category:
        return {
            "ok": False,
            "needs_input": True,
            "missing": [k for k, v in {"city": city, "category": category}.items() if not v],
            "prompt": "Tell me the city and business category (e.g. Dehradun + Gym).",
        }

    research = _list_research()
    c = city.lower()
    cat = category.lower()
    matches = [
        r
        for r in research
        if (r.get("city") or "").lower() == c and (r.get("category") or "").lower() == cat
    ]
    return {
        "ok": True,
        "city": city,
        "category": category,
        "leads": matches,
        "note": "Currently this uses saved research as the lead source. Next step is running the real local-lead-finder skill to generate new leads.",
    }


def _run_append(run_id: str, line: str) -> None:
    run = RUNS.get(run_id)
    if not run:
        return
    logs: list[str] = run.setdefault("logs", [])
    logs.append(line.rstrip("\n"))
    # cap logs to avoid unbounded growth
    if len(logs) > 2000:
        del logs[:500]


def _try_parse_embedded_json(run: dict) -> None:
    if run.get("result_json") is not None:
        return
    raw: str = run.get("_json_buf") or ""
    if not raw.strip():
        return
    try:
        run["result_json"] = json.loads(raw)
    except Exception:
        run["result_json"] = None


def _spawn_cmd_run(run_id: str, cmd: list[str], *, cwd: Path | None = None) -> None:
    run = RUNS.get(run_id)
    if not run:
        return

    run["cmd"] = " ".join(cmd)
    run["started_at"] = datetime.now().isoformat()
    run["status"] = "running"
    _run_append(run_id, f"$ {run['cmd']}")

    try:
        p = subprocess.Popen(
            cmd,
            cwd=str(cwd or Path.home()),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as exc:  # noqa: BLE001
        run["status"] = "error"
        run["error"] = str(exc)
        _run_append(run_id, f"[error] {exc}")
        return

    run["pid"] = p.pid

    # Capture Hermes "json" dumps (used by lead finder) into run['result_json'].
    json_mode = False
    depth = 0
    buf: list[str] = []

    assert p.stdout is not None
    for line in p.stdout:
        _run_append(run_id, line)
        s = line.strip()

        if not json_mode and s == "json":
            json_mode = True
            depth = 0
            buf = []
            continue

        if json_mode:
            if depth == 0 and not (s.startswith("{") or s.startswith("[")):
                continue
            buf.append(line)
            for ch in line:
                if ch in "{[":
                    depth += 1
                elif ch in "}]":
                    depth = max(0, depth - 1)
            if depth == 0 and buf:
                run["_json_buf"] = "".join(buf)
                _try_parse_embedded_json(run)
                json_mode = False
            continue

        if s.startswith("{") and s.endswith("}"):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, dict) and ("ok" in parsed or "url" in parsed):
                    run["result_json"] = parsed
            except Exception:
                pass

    rc = p.wait()
    run["exit_code"] = rc
    run["ended_at"] = datetime.now().isoformat()
    run["status"] = "done" if rc == 0 else "error"
    _run_append(run_id, f"[exit] {rc}")


def _spawn_hermes_chat_run(run_id: str, *, skill: str, prompt: str) -> None:
    cmd = ["hermes", "chat", "-s", skill, "--ignore-rules", "--cli", "-q", prompt]
    _spawn_cmd_run(run_id, cmd, cwd=Path.home())


@app.post("/api/pipeline/run/start")
def pipeline_run_start(req: RunStartRequest) -> dict:
    kind = (req.kind or "").strip()
    if kind not in {"lead_finder", "research", "demo_build", "demo_publish", "pitch"}:
        return {"ok": False, "error": "unsupported kind"}

    city = (req.city or "").strip()
    category = (req.category or "").strip()
    business = (req.business or "").strip()
    slug = (req.slug or "").strip()
    template = (req.template or "").strip()
    limit = int(req.limit or 10)

    run_id = uuid.uuid4().hex
    RUNS[run_id] = {"id": run_id, "kind": kind, "status": "queued", "logs": [], "created_at": datetime.now().isoformat()}

    def start_thread(fn, kwargs):
        t = threading.Thread(target=fn, args=(run_id,), kwargs=kwargs, daemon=True)
        t.start()
        RUNS[run_id]["thread_started"] = True

    if kind == "lead_finder":
        if not city or not category:
            return {
                "ok": False,
                "needs_input": True,
                "missing": [k for k, v in {"city": city, "category": category}.items() if not v],
                "prompt": "Tell me the city and business category (e.g. Dehradun + Gym).",
            }
        prompt = f"City: {city}, Category: {category}. Find {limit} leads only. Return structured JSON for each lead (business, city, category, issues, suggested_services) then a brief summary."
        start_thread(_spawn_hermes_chat_run, {"skill": "local-lead-finder", "prompt": prompt})
        return {"ok": True, "run_id": run_id}

    if kind == "research":
        if not business or not city or not category:
            return {
                "ok": False,
                "needs_input": True,
                "missing": [k for k, v in {"business": business, "city": city, "category": category}.items() if not v],
                "prompt": "Select a lead (business/city/category) first.",
            }
        prompt = f"{business}, {city}. Category: {category}. Research deeply and save lead-research.json."
        start_thread(_spawn_hermes_chat_run, {"skill": "lead-research", "prompt": prompt})
        return {"ok": True, "run_id": run_id}

    build_sh = LEAD_DEMO_SKILL_DIR / "scripts" / "build.sh"
    publish_py = LEAD_DEMO_SKILL_DIR / "scripts" / "publish_to_pages.py"

    if kind == "demo_build":
        if not slug:
            return {"ok": False, "needs_input": True, "missing": ["slug"], "prompt": "Need slug to build demo."}
        if not build_sh.is_file():
            return {"ok": False, "error": f"build script not found: {build_sh}"}
        cmd = ["bash", str(build_sh), slug]
        if template:
            cmd.append(template)
        start_thread(_spawn_cmd_run, {"cmd": cmd, "cwd": LEAD_DEMO_SKILL_DIR})
        return {"ok": True, "run_id": run_id}

    if kind == "demo_publish":
        if not slug:
            return {"ok": False, "needs_input": True, "missing": ["slug"], "prompt": "Need slug to publish demo."}
        if not publish_py.is_file():
            return {"ok": False, "error": f"publish script not found: {publish_py}"}
        cmd = ["python3", str(publish_py), slug]
        start_thread(_spawn_cmd_run, {"cmd": cmd, "cwd": LEAD_DEMO_SKILL_DIR})
        return {"ok": True, "run_id": run_id}

    # kind == "pitch"
    if not slug:
        return {"ok": False, "needs_input": True, "missing": ["slug"], "prompt": "Need slug to generate pitch."}
    prompt = f"Generate a concise outreach pitch for lead slug: {slug}. Use demo_url if present."
    start_thread(_spawn_hermes_chat_run, {"skill": "pitch-generator", "prompt": prompt})
    return {"ok": True, "run_id": run_id}


@app.get("/api/pipeline/run/{run_id}")
def pipeline_run_get(run_id: str, offset: int = 0) -> dict:
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="run not found")
    logs: list[str] = run.get("logs") or []
    off = max(0, int(offset))
    chunk = logs[off:]
    return {
        "ok": True,
        "run": {k: v for k, v in run.items() if k != "logs"},
        "logs": chunk,
        "next_offset": off + len(chunk),
    }


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="info")
