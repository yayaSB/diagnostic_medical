import os
import uuid
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.tools.patient_tools import generate_dynamic_question, QUESTIONS
from backend.app.tools.care_tools import recommend_interim_care
from backend.app.tools.mcp_client import get_red_flags_reference, search_medical_context
from backend.app.tools.urgency_scorer import calculate_urgency_score
from backend.app.tools.medical_sources import get_medical_sources
from backend.app.llm import call_openai, consensus_medical

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

class ImageAnalysisRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")

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

def should_stop_early(answers: list[str], case: str) -> tuple[bool, str]:
    """Determine if we can stop before 5 questions."""
    
    joined = " ".join([case, *answers]).lower()
    
    # Urgent cases
    urgent_patterns = [
        ("perte de conscience", "🚨 URGENCE: Perte de conscience. Arrêt immédiat."),
        ("arret cardiaque", "🚨 URGENCE: Arrêt cardiaque. Arrêt immédiat."),
        ("hemorragie massive", "🚨 URGENCE: Hémorragie massive. Arrêt immédiat."),
        ("intoxication grave", "🚨 URGENCE: Intoxication. Arrêt immédiat."),
        ("crise epileptique", "🚨 URGENCE: Crise épileptique. Arrêt immédiat."),
    ]
    
    for pattern, reason in urgent_patterns:
        if pattern in joined:
            return True, reason
    
    # Benign obvious cases
    benign_patterns = [
        ("mal de tete leger", "✅ STOP: Céphalée légère. Conseils suffisants."),
        ("petit coup de fatigue", "✅ STOP: Fatigue passagère. Repos suffisant."),
        ("griffure legere", "✅ STOP: Blessure mineure. Soins locaux suffisants."),
    ]
    
    for pattern, reason in benign_patterns:
        if pattern in joined:
            return True, reason
    
    return False, ""


def _generate_summary(case: str, questions: list, answers: list, interim: str, mcp_context: str, consensus: dict = None) -> str:
    """Generate clinical summary with OpenAI or fallback."""
    
    qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])
    
    consensus_text = ""
    if consensus and consensus.get("avis_gpt", {}).get("response"):
        consensus_text = f"\nAvis GPT: {consensus['avis_gpt']['response'][:200]}...\nAvis Claude: {consensus['avis_claude']['response'][:200]}..."
    
    system_prompt = (
        "Tu es un assistant médical pédagogique avancé. Tu produis une synthèse clinique "
        "préliminaire structurée et intelligente. Tu analyses les symptômes, proposes un "
        "diagnostic différentiel prudent, et orientes. Maximum 10 phrases. Langue: français."
    )
    
    user_prompt = (
        f"Cas initial: {case}\n\n"
        f"Questions-réponses:\n{qa_text}\n\n"
        f"Recommandation intermédiaire: {interim}\n\n"
        f"Contexte MCP:\n{mcp_context[:400]}\n"
        f"{consensus_text}\n\n"
        "Rédige une synthèse avec:\n"
        "1. Résumé du cas\n"
        "2. Diagnostic différentiel (2-3 hypothèses avec confiance)\n"
        "3. Éléments de préoccupation\n"
        "4. Orientation recommandée"
    )

    llm_result = call_openai(system_prompt, user_prompt, temperature=0.3)
    if llm_result:
        return llm_result
    
    # Fallback
    return (
        f"Synthèse (mode local): Patient '{case}'. {len(answers)} questions. "
        f"Recommandation: {interim[:100]}..."
    )


def _generate_report(case: str, summary: str, interim: str, treatment: str, notes: str, mcp_context: str, sources: list, urgency: dict) -> str:
    """Generate final report with OpenAI or fallback."""
    
    sources_text = "\n".join([f"- [{s['type']}] {s['title']}: {s['url']}" for s in sources]) if sources else "Aucune"
    
    system_prompt = (
        "Tu es un assistant médical pédagogique. Rapport final professionnel, "
        "structuré, avec contenu original à chaque section. Pas de répétition. "
        "Mention éthique obligatoire. Langue: français."
    )
    
    user_prompt = (
        f"Cas: {case}\n\n"
        f"Synthèse: {summary}\n\n"
        f"Recommandation: {interim}\n\n"
        f"Score urgence: {urgency['score']}/100 ({urgency['label']})\n"
        f"Contexte: {mcp_context[:300]}\n\n"
        f"Traitement médecin: {treatment}\n"
        f"Notes: {notes or 'Aucune'}\n\n"
        f"Sources: {sources_text}\n\n"
        "Rédige un rapport final avec ces sections DISTINCTES:\n"
        "# MOTIF DE CONSULTATION\n"
        "# ANAMNÈSE\n"
        "# SYNTHÈSE CLINIQUE\n"
        "# DIAGNOSTIC DIFFÉRENTIEL\n"
        "# RECOMMANDATIONS\n"
        "# DÉCISION MÉDICALE\n"
        "# SURVEILLANCE\n"
        "# SOURCES\n"
        "# MENTION ÉTHIQUE"
    )

    llm_result = call_openai(system_prompt, user_prompt, temperature=0.2)
    if llm_result:
        return llm_result
    
    # Fallback
    return f"""RAPPORT FINAL - Orientation Clinique
=====================================

CAS: {case}
SYNTHÈSE: {summary}
RECOMMANDATION: {interim}
SCORE URGENCE: {urgency['score']}/100 - {urgency['label']}
REVUE MÉDECIN: {treatment}
NOTES: {notes or 'Aucune'}

SOURCES:
{sources_text}

MENTION ÉTHIQUE: Ce système ne remplace pas une consultation médicale."""


def _build_response_payload(thread_id: str, session: dict) -> dict:
    """Build response for frontend."""
    count = session.get("question_count", 0)
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
    
    # Build interrupt
    interrupt = None
    
    if has_report or has_treatment:
        interrupt = None
    elif diagnostic and not has_treatment:
        mcp_affiche = session.get("mcp_search", "")
        
        interrupt = {
            "type": "physician_review",
            "diagnostic_summary": diagnostic,
            "interim_care": session.get("interim_care", ""),
            "mcp_context": mcp_affiche,
            "urgency": session.get("urgency"),
            "consensus": session.get("consensus")
        }
    elif count > 0 and count <= 5:
        current_q_index = count - 1
        
        if current_q_index < len(session.get("questions", [])):
            question_text = session["questions"][current_q_index]
        elif current_q_index < len(QUESTIONS):
            question_text = f"Question {count}/5: {QUESTIONS[current_q_index]}"
        else:
            question_text = "Question finale"
        
        interrupt = {
            "type": "patient_question",
            "question": question_text,
            "question_number": count
        }
    
    # Calculate urgency if we have answers
    urgency = None
    if session.get("patient_answers"):
        urgency = calculate_urgency_score(
            session.get("initial_case", ""),
            session.get("patient_answers", [])
        )
    
    return {
        "thread_id": thread_id,
        "status": status,
        "interrupt": interrupt,
        "urgency": urgency,
        "state": {
            "question_count": count,
            "patient_answers": session.get("patient_answers", []),
            "questions": session.get("questions", []),
            "diagnostic_summary": diagnostic or None,
            "interim_care": session.get("interim_care") or None,
            "physician_treatment": session.get("physician_treatment") or None,
            "physician_notes": session.get("physician_notes") or None,
            "final_report": session.get("final_report") or None,
            "mcp_context": session.get("mcp_search") or None,
            "sources": session.get("sources") or None,
            "urgency": urgency,
            "consensus": session.get("consensus") or None,
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
        "mcp_ref": "",
        "mcp_search": "",
        "mcp_context": "",
        "sources": [],
        "urgency": None,
        "consensus": None,
    }
    
    sessions[thread_id] = session
    
    # Generate Q1 dynamically with AI
    question = generate_dynamic_question(request.patient_case, [], 0)
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
    
    # Guard: already 5 answers
    if len(answers) >= 5:
        return _build_response_payload(request.thread_id, session)
    
    # Store answer
    answers.append(request.answer)
    session["patient_answers"] = answers
    
    # Check early stopping
    should_stop, stop_reason = should_stop_early(answers, session.get("initial_case", ""))
    
    if should_stop:
        case = session.get("initial_case", "")
        questions = session.get("questions", [])
        
        mcp_ref = get_red_flags_reference()
        mcp_search = search_medical_context(case, answers)
        interim = recommend_interim_care(case, answers, mcp_search)
        
        session["mcp_ref"] = mcp_ref
        session["mcp_search"] = mcp_search
        
        # Get consensus from dual AI
        consensus = consensus_medical(case, questions, answers)
        session["consensus"] = consensus
        
        summary = f"{stop_reason}\n\n" + _generate_summary(case, questions, answers, interim, mcp_search, consensus)
        
        session["interim_care"] = interim
        session["diagnostic_summary"] = summary
        
        return _build_response_payload(request.thread_id, session)
    
    # Ask next question if under 5
    if count < 5:
        case = session.get("initial_case", "")
        question = generate_dynamic_question(case, answers, count)
        
        session["questions"] = session.get("questions", []) + [question]
        session["question_count"] = count + 1
        return _build_response_payload(request.thread_id, session)
    
    # All 5 questions answered, generate summary
    case = session.get("initial_case", "")
    questions = session.get("questions", [])
    
    mcp_ref = get_red_flags_reference()
    mcp_search = search_medical_context(case, answers)
    interim = recommend_interim_care(case, answers, mcp_search)
    
    session["mcp_ref"] = mcp_ref
    session["mcp_search"] = mcp_search
    
    # Get consensus from dual AI
    consensus = consensus_medical(case, questions, answers)
    session["consensus"] = consensus
    
    summary = _generate_summary(case, questions, answers, interim, mcp_search, consensus)
    
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
    mcp_search = session.get("mcp_search", "")
    urgency = session.get("urgency", {})
    
    # Get medical sources
    sources = get_medical_sources(case)
    session["sources"] = sources
    
    report = _generate_report(
        case, summary, interim, 
        request.treatment, request.notes or "",
        mcp_search, sources, urgency
    )
    
    session["final_report"] = report
    
    return _build_response_payload(thread_id, session)


@app.post("/analyze-image")
async def analyze_image(data: ImageAnalysisRequest):
    """Analyze medical image with GPT-4 Vision."""
    image_b64 = data.image
    
    if not image_b64:
        raise HTTPException(status_code=400, detail="Image manquante")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"description": "Analyse image non disponible (clé API manquante)"}
    
    try:
        import requests
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Décris ce symptôme médical visible sur cette photo. Sois concis (2-3 phrases). Mentionne si c'est urgent et quels signes d'alerte surveiller."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            }
        )
        
        result = response.json()
        description = result["choices"][0]["message"]["content"]
        return {"description": description}
        
    except Exception as e:
        return {"description": f"Erreur analyse: {str(e)}"}


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