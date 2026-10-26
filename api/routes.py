# Seven RPG — API Routes (FastAPI placeholder)
# Directive: multi-agent-architect — expose agent system via FastAPI (optional).
# Directive: codex-fable5 — verify before completion; no secrets in code.
# Status: Placeholder — implement after stack selection (G2 exit).

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

app = FastAPI(title="Seven RPG API", version="0.1.0")


class RunRequest(BaseModel):
    goal: str
    session_id: str


class RunResponse(BaseModel):
    result: Dict[str, Any]
    commit_sha: Optional[str] = None


@app.get("/health")
async def health() -> Dict[str, str]:
    """Health check — verifies API is running."""
    return {"status": "ok", "service": "seven-rpg"}


@app.post("/run", response_model=RunResponse)
async def run_agent(req: RunRequest) -> RunResponse:
    """
    Execute the Seven RPG agent graph.
    Placeholder — wire to graphs.workflow.run after stack selection.
    """
    # TODO: Import and call graphs.workflow.run(req.goal, req.session_id)
    # after G2 stack decision and langgraph installation.
    raise HTTPException(
        status_code=501,
        detail="Not implemented — await stack selection (ADR-0001) and langgraph install.",
    )


@app.get("/state/{session_id}")
async def get_state(session_id: str) -> Dict[str, Any]:
    """Retrieve saved state for a session (placeholder)."""
    raise HTTPException(
        status_code=501,
        detail="Not implemented — await persistence layer (G3).",
    )


@app.get("/")
async def root() -> Dict[str, str]:
    return {
        "service": "Seven RPG",
        "version": "0.1.0",
        "status": "planning/bootstrap",
        "docs": "/docs",
    }