from langgraph.types import interrupt

from app.llm import call_openai
from app.state import MedicalState
from app.tools.care_tools import recommend_interim_care
from app.tools.mcp_client import get_red_flags_reference
from app.tools.patient_tools import ask_patient


def _fallback_summary(initial_case: str, questions: list[str], answers: list[str]) -> str:
    return (
        "Synthèse clinique préliminaire :\n"
        f"- Cas initial : {initial_case or 'Non renseigné'}\n"
        + "\n".join(f"- Q{i + 1}: {questions[i]} Réponse: {answers[i]}" for i in range(5))
        + "\n\nCette synthèse est une orientation clinique préliminaire et ne constitue pas un diagnostic définitif."
    )


def _generate_summary(initial_case: str, questions: list[str], answers: list[str], mcp_context: str) -> str:
    patient_dialog = "\n".join(f"Question {i + 1}: {questions[i]}\nRéponse: {answers[i]}" for i in range(5))
    llm_summary = call_openai(
        system_prompt=(
            "Tu es un agent pédagogique d'orientation clinique préliminaire. "
            "Tu ne fournis jamais de diagnostic définitif. "
            "Tu rédiges en français, avec prudence, sous forme structurée."
        ),
        user_prompt=(
            "À partir du cas patient et des réponses, rédige une synthèse clinique préliminaire courte. "
            "Mentionne les éléments importants, les signes d'alerte éventuels et rappelle que cela ne remplace pas "
            "une consultation médicale.\n\n"
            f"Cas initial:\n{initial_case}\n\n"
            f"Questions/réponses:\n{patient_dialog}\n\n"
            f"Référence de sécurité MCP:\n{mcp_context}"
        ),
    )
    return llm_summary or _fallback_summary(initial_case, questions, answers)


def diagnostic_agent(state: MedicalState) -> MedicalState:
    answers: list[str] = []
    questions: list[str] = []

    for index in range(5):
        question = ask_patient(index)
        response = interrupt(
            {
                "type": "patient_question",
                "question_number": index + 1,
                "total_questions": 5,
                "question": question,
            }
        )
        questions.append(question)
        answers.append(str(response))

    mcp_context = get_red_flags_reference()
    summary = _generate_summary(state.get("initial_case", ""), questions, answers, mcp_context)

    return {
        "questions": questions,
        "patient_answers": answers,
        "question_count": 5,
        "diagnostic_summary": summary,
        "interim_care": recommend_interim_care(state.get("initial_case", ""), answers, mcp_context),
    }
