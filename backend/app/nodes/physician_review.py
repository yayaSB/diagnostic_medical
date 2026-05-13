from langchain_core.messages import SystemMessage, HumanMessage
from backend.app.state import MedicalState

class PhysicianReviewNode:
    def __call__(self, state: MedicalState) -> MedicalState:
        messages = state.get("messages", [])
        diagnostic_summary = state.get("diagnostic_summary", "")
        interim_care = state.get("interim_care", "")
        
        review_message = f"""REVUE MEDECIN REQUISE

Synthese clinique preliminaire:
{diagnostic_summary}

Recommandation intermediaire:
{interim_care}

Veuillez proposer un traitement ou une conduite a tenir avant la generation du rapport final.

Ce systeme ne remplace pas une consultation medicale."""
        
        new_messages = messages + [
            SystemMessage(content="[Physician Review] En attente de validation medecin."),
            HumanMessage(content=review_message)
        ]
        
        return {
            **state,
            "messages": new_messages,
            "status": "waiting_physician",
        }
