"""Chat UI server — FastAPI + agent loop."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from hermes_app.agent.loop import AgentLoop

STATIC_DIR = Path(__file__).resolve().parents[3] / "web" / "static"
app = FastAPI(title="Hermes Agent App", version="0.3.0")
agent = AgentLoop()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    report_updated: bool
    tools_used: list[str]


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


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


if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def run(host: str = "127.0.0.1", port: int = 8765) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port, log_level="info")
