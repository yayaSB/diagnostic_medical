import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.graph import medical_graph
from backend.app.state import MedicalState

os.environ.setdefault("OPENAI_API_KEY", "")

class StartSessionRequest(BaseModel):
    patient_case: str = Field(..., description="Description initiale du cas patient")

class PatientAnswerRequest(BaseModel):
    thread_id: str
    answer: str = Field(..., description="Reponse du patient")

class PhysicianReviewRequest(BaseModel):
    thread_id: str
    treatment: str = Field(..., description="Traitement ou conduite a tenir")
    notes: Optional[str] = Field(None, description="Notes additionnelles")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Medical Multi-Agent API demarree")
    yield
    print("API arretee")

app = FastAPI(
    title="Medical Multi-Agent API",
    description="API pour le systeme d'orientation clinique multi-agents",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}

@app.post("/sessions/start")
async def start_session(request: StartSessionRequest):
    thread_id = str(uuid.uuid4())
    
    initial_state: MedicalState = {
        "messages": [],
        "next": "diagnostic_agent",
        "question_count": 0,
        "patient_case": request.patient_case,
        "patient_responses": [],
        "interim_care": "",
        "diagnostic_summary": "",
        "physician_treatment": "",
        "physician_notes": "",
        "final_report": "",
        "thread_id": thread_id,
        "status": "started"
    }
    
    sessions[thread_id] = initial_state
    
    return {
        "thread_id": thread_id,
        "status": "started",
        "message": "Session demarree. Utilisez /consultation/start pour commencer le diagnostic."
    }

@app.post("/consultation/start")
async def start_consultation(request: StartSessionRequest):
    thread_id = str(uuid.uuid4())
    
    initial_state: MedicalState = {
        "messages": [],
        "next": "diagnostic_agent",
        "question_count": 0,
        "patient_case": request.patient_case,
        "patient_responses": [],
        "interim_care": "",
        "diagnostic_summary": "",
        "physician_treatment": "",
        "physician_notes": "",
        "final_report": "",
        "thread_id": thread_id,
        "status": "in_progress"
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    result = medical_graph.invoke(initial_state, config)
    sessions[thread_id] = result
    
    current_question = None
    for msg in reversed(result.get("messages", [])):
        if hasattr(msg, 'content') and "Question" in msg.content:
            current_question = msg.content
            break
    
    return {
        "thread_id": thread_id,
        "status": result.get("status", "in_progress"),
        "question_number": result.get("question_count", 0),
        "current_question": current_question,
        "message": "Consultation demarree. Veuillez repondre a la question."
    }

@app.post("/consultation/resume")
async def resume_consultation(request: PatientAnswerRequest):
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    state = sessions[request.thread_id]
    question_count = state.get("question_count", 0)
    
    last_question = ""
    for msg in reversed(state.get("messages", [])):
        if hasattr(msg, 'content') and "Question" in msg.content:
            last_question = msg.content
            break
    
    state["patient_responses"] = state.get("patient_responses", []) + [{
        "question": last_question,
        "answer": request.answer
    }]
    
    from langchain_core.messages import HumanMessage
    state["messages"] = state.get("messages", []) + [
        HumanMessage(content=f"Reponse patient: {request.answer}")
    ]
    
    config = {"configurable": {"thread_id": request.thread_id}}
    
    try:
        result = medical_graph.invoke(state, config)
        sessions[request.thread_id] = result
        
        status = result.get("status", "in_progress")
        question_count = result.get("question_count", 0)
        diagnostic_summary = result.get("diagnostic_summary", "")
        
        current_question = None
        for msg in reversed(result.get("messages", [])):
            if hasattr(msg, 'content'):
                if "Question" in msg.content and question_count < 5:
                    current_question = msg.content
                    break
                elif "REVUE MEDECIN" in msg.content:
                    status = "waiting_physician"
                    break
                elif "RAPPORT FINAL" in msg.content:
                    status = "completed"
                    break
        
        response = {
            "thread_id": request.thread_id,
            "status": status,
            "question_number": question_count,
            "current_question": current_question,
            "diagnostic_summary": diagnostic_summary if diagnostic_summary else None,
            "interim_care": result.get("interim_care") if result.get("interim_care") else None,
        }
        
        if status == "waiting_physician":
            response["message"] = "En attente de la revue du medecin."
        elif status == "completed":
            response["message"] = "Consultation terminee."
        else:
            response["message"] = f"Question {question_count}/5. Veuillez repondre."
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.post("/consultation/{thread_id}/physician-review")
async def submit_physician_review(thread_id: str, request: PhysicianReviewRequest):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    state = sessions[thread_id]
    
    if not state.get("diagnostic_summary"):
        raise HTTPException(status_code=400, detail="Synthese non disponible")
    
    state["physician_treatment"] = request.treatment
    state["physician_notes"] = request.notes or ""
    state["status"] = "physician_reviewed"
    
    from langchain_core.messages import HumanMessage
    state["messages"] = state.get("messages", []) + [
        HumanMessage(content=f"[Medecin] Traitement propose: {request.treatment}")
    ]
    if request.notes:
        state["messages"].append(HumanMessage(content=f"[Medecin] Notes: {request.notes}"))
    
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        result = medical_graph.invoke(state, config)
        sessions[thread_id] = result
        
        return {
            "thread_id": thread_id,
            "status": "completed",
            "message": "Rapport final genere.",
            "final_report": result.get("final_report", "")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

@app.get("/consultation/{thread_id}")
async def get_consultation_status(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    state = sessions[thread_id]
    
    current_question = None
    for msg in reversed(state.get("messages", [])):
        if hasattr(msg, 'content') and "Question" in msg.content:
            current_question = msg.content
            break
    
    formatted_messages = []
    for msg in state.get("messages", []):
        if hasattr(msg, 'content'):
            formatted_messages.append({
                "role": getattr(msg, 'type', 'unknown'),
                "content": msg.content
            })
    
    return {
        "thread_id": thread_id,
        "status": state.get("status", "unknown"),
        "question_count": state.get("question_count", 0),
        "current_question": current_question,
        "diagnostic_summary": state.get("diagnostic_summary") or None,
        "interim_care": state.get("interim_care") or None,
        "physician_treatment": state.get("physician_treatment") or None,
        "final_report": state.get("final_report") or None,
        "messages": formatted_messages
    }

@app.get("/consultation/{thread_id}/report")
async def get_final_report(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    state = sessions[thread_id]
    
    if not state.get("final_report"):
        raise HTTPException(status_code=400, detail="Rapport non disponible")
    
    return {
        "thread_id": thread_id,
        "final_report": state["final_report"],
        "status": "completed"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "medical-multi-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)