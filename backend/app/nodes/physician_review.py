from langgraph.types import interrupt

from app.state import MedicalState


def physician_review(state: MedicalState) -> MedicalState:
    treatment = interrupt(
        {
            "type": "physician_review",
            "diagnostic_summary": state.get("diagnostic_summary", ""),
            "interim_care": state.get("interim_care", ""),
            "prompt": "Veuillez saisir le traitement ou la conduite à tenir proposée par le médecin traitant.",
        }
    )
    return {"physician_treatment": str(treatment)}
