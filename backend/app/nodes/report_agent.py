from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from backend.app.state import MedicalState

class ReportAgentNode:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    
    def __call__(self, state: MedicalState) -> MedicalState:
        messages = state.get("messages", [])
        patient_case = state.get("patient_case", "")
        patient_responses = state.get("patient_responses", [])
        diagnostic_summary = state.get("diagnostic_summary", "")
        interim_care = state.get("interim_care", "")
        physician_treatment = state.get("physician_treatment", "")
        physician_notes = state.get("physician_notes", "")
        
        report = self._generate_report(
            patient_case, patient_responses, diagnostic_summary,
            interim_care, physician_treatment, physician_notes
        )
        
        new_messages = messages + [
            SystemMessage(content="[Report Agent] Rapport final genere."),
            HumanMessage(content=f"RAPPORT FINAL

{report}")
        ]
        
        return {
            **state,
            "messages": new_messages,
            "final_report": report,
            "status": "completed",
        }
    
    def _generate_report(self, case, responses, summary, care, treatment, notes):
        context = f"Cas initial: {case}

Reponses patient:
"
        for i, resp in enumerate(responses, 1):
            context += f"{i}. {resp.get('question', '')} -> {resp.get('answer', '')}
"
        
        prompt = f"""Generez un rapport medical structure au format suivant:

# RAPPORT D'ORIENTATION CLINIQUE

## 1. INFORMATIONS PATIENT
- Cas rapporte: [resume]

## 2. QUESTIONS ET REPONSES
[Liste des 5 Q/R]

## 3. SYNTHESE CLINIQUE PRELIMINAIRE
{summary}

## 4. RECOMMANDATION INTERMEDIAIRE
{care}

## 5. AVIS DU MEDECIN TRAITANT
{treatment}

## 6. CONCLUSION

---
AVERTISSEMENT IMPORTANT : Ce systeme est un exercice academique et ne remplace pas une consultation medicale. Ce rapport ne constitue pas un diagnostic definitif.

Donnees brutes:
{context}"""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
