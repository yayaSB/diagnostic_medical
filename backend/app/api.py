from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.types import Command
from pydantic import BaseModel

from app.graph import graph

app = FastAPI(title="Medical Multi-Agent Orientation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StartRequest(BaseModel):
    initial_case: str


class ResumeRequest(BaseModel):
    thread_id: str
    answer: str


def _config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


def _serialize(thread_id: str, result: dict | None = None) -> dict:
    snapshot = graph.get_state(_config(thread_id))
    interrupts = [item.value for item in snapshot.interrupts]
    values = dict(snapshot.values or {})
    return {
        "thread_id": thread_id,
        "status": "interrupted" if interrupts else "completed",
        "interrupt": interrupts[0] if interrupts else None,
        "state": values,
        "result": result,
    }


@app.post("/sessions/start")
def sessions_start() -> dict:
    return {"thread_id": str(uuid4())}


@app.post("/consultation/start")
def consultation_start(payload: StartRequest) -> dict:
    thread_id = str(uuid4())
    graph.invoke({"thread_id": thread_id, "initial_case": payload.initial_case}, _config(thread_id))
    return _serialize(thread_id)


@app.post("/consultation/resume")
def consultation_resume(payload: ResumeRequest) -> dict:
    snapshot = graph.get_state(_config(payload.thread_id))
    if snapshot.values is None:
        raise HTTPException(status_code=404, detail="Consultation introuvable")
    result = graph.invoke(Command(resume=payload.answer), _config(payload.thread_id))
    return _serialize(payload.thread_id, result)


@app.get("/consultation/{thread_id}")
def consultation_get(thread_id: str) -> dict:
    snapshot = graph.get_state(_config(thread_id))
    if snapshot.values is None:
        raise HTTPException(status_code=404, detail="Consultation introuvable")
    return _serialize(thread_id)


@app.get("/consultation/{thread_id}/report")
def consultation_report(thread_id: str) -> dict:
    snapshot = graph.get_state(_config(thread_id))
    if snapshot.values is None:
        raise HTTPException(status_code=404, detail="Consultation introuvable")
    report = snapshot.values.get("final_report")
    if not report:
        raise HTTPException(status_code=409, detail="Le rapport final n'est pas encore disponible")
    return {"thread_id": thread_id, "final_report": report}
