from langchain_core.messages import AIMessage

from backend.app.state import MedicalState
from backend.app.tools.patient_tools import ask_patient
from backend.app.tools.care_tools import recommend_interim_care
from backend.app.tools.mcp_client import get_red_flags_reference
from backend.app.llm import call_openai


class DiagnosticAgentNode:
    def __call__(self, state: MedicalState) -> MedicalState:
        count = state.get("question_count", 0)

        # If we've already asked 5 questions, generate summary and STOP
        if count >= 5:
            answers = state.get("patient_answers", [])
            questions = state.get("questions", [])
            case = state.get("initial_case", "")

            mcp_ref = get_red_flags_reference()
            interim = recommend_interim_care(case, answers, mcp_ref)

            summary = self._generate_summary(case, questions, answers, interim)

            state["interim_care"] = interim
            state["diagnostic_summary"] = summary
            state["messages"] = state.get("messages", []) + [
                AIMessage(content="REVUE MEDECIN: Synthese complete. En attente validation.")
            ]
            return state

        # Ask next question
        question = ask_patient(count)
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Question {count+1}/5: {question}")
        ]
        state["questions"] = state.get("questions", []) + [question]
        state["question_count"] = count + 1
        
        return state

    def _generate_summary(self, case: str, questions: list, answers: list, interim: str) -> str:
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

        return (
            f"Synthese preliminaire (mode local): Le patient decrit '{case}'. "
            f"Apres {len(answers)} questions, la recommandation est: {interim}"
        )