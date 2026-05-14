from langchain_core.messages import AIMessage

from backend.app.state import MedicalState
from backend.app.llm import call_openai


class ReportAgentNode:
    def __call__(self, state: MedicalState) -> MedicalState:
        report = self._generate_report(state)
        state["final_report"] = report
        state["messages"] = state.get("messages", []) + [
            AIMessage(content="RAPPORT FINAL genere.")
        ]
        return state

    def _generate_report(self, state: MedicalState) -> str:
        system_prompt = (
            "Tu es un assistant medical pedagogique. Tu rediges un rapport final "
            "structure et professionnel. Tu ne diagnosticques pas. Tu inclus "
            "toujours la mention ethique obligatoire."
        )
        user_prompt = (
            f"Cas initial: {state.get('initial_case', 'N/A')}\n\n"
            f"Synthese clinique preliminaire:\n{state.get('diagnostic_summary', 'N/A')}\n\n"
            f"Recommandation intermediaire:\n{state.get('interim_care', 'N/A')}\n\n"
            f"Revue medecin traitant:\n"
            f"- Traitement: {state.get('physician_treatment', 'N/A')}\n"
            f"- Notes: {state.get('physician_notes', 'N/A')}\n\n"
            "Redige un rapport final complet avec sections claires. "
            "Termine par la mention: 'Ce systeme ne remplace pas une consultation medicale.'"
        )

        llm_result = call_openai(system_prompt, user_prompt, temperature=0.2)
        if llm_result:
            return llm_result

        return f"""RAPPORT FINAL - Orientation Clinique
=====================================

CAS INITIAL
-----------
{state.get('initial_case', 'N/A')}

SYNTHÈSE CLINIQUE PRÉLIMINAIRE
------------------------------
{state.get('diagnostic_summary', 'N/A')}

RECOMMANDATION INTERMÉDIAIRE
----------------------------
{state.get('interim_care', 'N/A')}

REVUE MÉDECIN TRAITANT
----------------------
Traitement proposé : {state.get('physician_treatment', 'N/A')}
Notes additionnelles : {state.get('physician_notes', 'N/A')}

MENTION ÉTHIQUE
---------------
Ce système ne remplace pas une consultation médicale.
"""