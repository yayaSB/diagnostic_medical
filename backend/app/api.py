import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.tools.patient_tools import ask_patient, QUESTIONS
from backend.app.tools.care_tools import recommend_interim_care
from backend.app.tools.mcp_client import get_red_flags_reference
from backend.app.llm import call_openai

os.environ.setdefault("OPENAI_API_KEY", "")

class StartConsultationRequest(BaseModel):
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

def _generate_summary(case: str, questions: list, answers: list, interim: str) -> str:
    qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])
    system_prompt = (
        "Tu es un assistant medical pedagogique. Tu produis une synthese clinique "
        "preliminaire concise et prudente. Tu ne diagnosticques pas. Tu utilises "
        "un langage neutre et recommandes toujours une consultation medicale."
    )
    user_prompt = (
        f"Cas initial: {case}\n\n"
        f"Questions et reponses:\n{qa_text}\n\n"
        f"Recommandation intermediaire: {interim}\n\n"
        "Redige une synthese clinique preliminaire de 3 a 5 phrases."
    )
    llm_result = call_openai(system_prompt, user_prompt, temperature=0.3)
    if llm_result:
        return llm_result
    return f"Synthese preliminaire (mode local): Le patient decrit '{case}'. Apres {len(answers)} questions, la recommandation est: {interim}"

def _generate_report(case: str, summary: str, interim: str, treatment: str, notes: str) -> str:
    system_prompt = (
        "Tu es un assistant medical pedagogique. Tu rediges un rapport final "
        "structure et professionnel. Tu ne diagnosticques pas. Tu inclus "
        "toujours la mention ethique obligatoire."
    )
    user_prompt = (
        f"Cas initial: {case}\n\n"
        f"Synthese clinique preliminaire:\n{summary}\n\n"
        f"Recommandation intermediaire:\n{interim}\n\n"
        f"Revue medecin traitant:\n"
        f"- Traitement: {treatment}\n"
        f"- Notes: {notes}\n\n"
        "Redige un rapport final complet avec sections claires. "
        "Termine par la mention: 'Ce systeme ne remplace pas une consultation medicale.'"
    )
    llm_result = call_openai(system_prompt, user_prompt, temperature=0.2)
    if llm_result:
        return llm_result
    return f"""RAPPORT FINAL - Orientation Clinique
=====================================
CAS INITIAL: {case}
SYNTHÈSE: {summary}
RECOMMANDATION: {interim}
REVUE MÉDECIN: Traitement: {treatment} | Notes: {notes}
MENTION ÉTHIQUE: Ce système ne remplace pas une consultation médicale."""

def _build_response_payload(thread_id: str, session: dict) -> dict:
    count = session.get("question_count", 0)  # How many questions ASKED so far
    answers_count = len(session.get("patient_answers", []))
    diagnostic = session.get("diagnostic_summary", "")
    has_report = bool(session.get("final_report"))
    has_treatment = bool(session.get("physician_treatment"))
    
    # Determine status
    status = "in_progress"
    if has_report:
        status = "completed"
    elif has_treatment:
        status = "physician_reviewed"
    elif diagnostic:
        status = "waiting_physician"
    
    # Build interrupt for frontend compatibility
    interrupt = None
    
    if has_report or has_treatment:
        interrupt = None  # Done
    elif diagnostic and not has_treatment:
        # Physician review needed
        interrupt = {
            "type": "physician_review",
            "diagnostic_summary": diagnostic,
            "interim_care": session.get("interim_care", "")
        }
    elif count > 0 and count <= 5:
        # Currently showing question number 'count' (1-5)
        # The question index is count - 1 (0-4)
        current_q_index = count - 1
        
        if current_q_index < len(QUESTIONS):
            question_text = f"Question {count}/5: {QUESTIONS[current_q_index]}"
            interrupt = {
                "type": "patient_question",
                "question": question_text,
                "question_number": count  # 1, 2, 3, 4, 5
            }
    
    return {
        "thread_id": thread_id,
        "status": status,
        "interrupt": interrupt,
        "state": {
            "question_count": count,
            "patient_answers": session.get("patient_answers", []),
            "questions": session.get("questions", []),
            "diagnostic_summary": diagnostic or None,
            "interim_care": session.get("interim_care") or None,
            "physician_treatment": session.get("physician_treatment") or None,
            "physician_notes": session.get("physician_notes") or None,
            "final_report": session.get("final_report") or None,
        }
    }

@app.post("/consultation/start")
async def start_consultation(request: StartConsultationRequest):
    thread_id = str(uuid.uuid4())
    
    session = {
        "thread_id": thread_id,
        "initial_case": request.patient_case,
        "questions": [],
        "patient_answers": [],
        "question_count": 0,
        "interim_care": "",
        "diagnostic_summary": "",
        "physician_treatment": "",
        "physician_notes": "",
        "final_report": "",
    }
    
    sessions[thread_id] = session
    
    # Ask first question (index 0, display as Question 1/5)
    question = ask_patient(0)
    session["questions"] = [question]
    session["question_count"] = 1
    
    return _build_response_payload(thread_id, session)

@app.post("/consultation/resume")
async def resume_consultation(request: PatientAnswerRequest):
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    session = sessions[request.thread_id]
    count = session.get("question_count", 0)
    answers = session.get("patient_answers", [])
    
    # GUARD: If already have 5 answers, don't accept more
    if len(answers) >= 5:
        # Just return current state without adding
        return _build_response_payload(request.thread_id, session)
    
    # Store answer
    answers.append(request.answer)
    session["patient_answers"] = answers
    
    # Check if we need to ask more questions
    if count < 5:
        next_q_index = count  # 1, 2, 3, 4 for Q2-Q5
        
        if next_q_index < len(QUESTIONS):
            question = ask_patient(next_q_index)
            session["questions"] = session.get("questions", []) + [question]
            session["question_count"] = count + 1
            return _build_response_payload(request.thread_id, session)
    
    # All 5 questions answered, generate summary
    case = session.get("initial_case", "")
    questions = session.get("questions", [])
    
    mcp_ref = get_red_flags_reference()
    interim = recommend_interim_care(case, answers, mcp_ref)
    summary = _generate_summary(case, questions, answers, interim)
    
    session["interim_care"] = interim
    session["diagnostic_summary"] = summary
    
    return _build_response_payload(request.thread_id, session)

@app.post("/consultation/{thread_id}/physician-review")
async def submit_physician_review(thread_id: str, request: PhysicianReviewRequest):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    session = sessions[thread_id]
    
    if not session.get("diagnostic_summary"):
        raise HTTPException(status_code=400, detail="Synthese non disponible")
    
    session["physician_treatment"] = request.treatment
    session["physician_notes"] = request.notes or ""
    
    # Generate final report
    case = session.get("initial_case", "")
    summary = session.get("diagnostic_summary", "")
    interim = session.get("interim_care", "")
    
    report = _generate_report(case, summary, interim, request.treatment, request.notes or "")
    
    session["final_report"] = report
    
    return _build_response_payload(thread_id, session)

@app.get("/consultation/{thread_id}")
async def get_consultation_status(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    return _build_response_payload(thread_id, sessions[thread_id])

@app.get("/consultation/{thread_id}/report")
async def get_final_report(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session non trouvee")
    
    session = sessions[thread_id]
    
    if not session.get("final_report"):
        raise HTTPException(status_code=400, detail="Rapport non disponible")
    
    return {
        "thread_id": thread_id,
        "final_report": session["final_report"],
        "status": "completed"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "medical-multi-agent"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)