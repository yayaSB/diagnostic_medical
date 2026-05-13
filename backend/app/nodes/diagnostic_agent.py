from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from backend.app.state import MedicalState
from backend.app.tools.patient_tools import ask_patient_tool
from backend.app.tools.care_tools import recommend_interim_care_tool

class DiagnosticAgentNode:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def __call__(self, state: MedicalState) -> MedicalState:
        messages = state.get("messages", [])
        question_count = state.get("question_count", 0)
        patient_case = state.get("patient_case", "")
        patient_responses = state.get("patient_responses", [])
        
        if question_count < 5:
            question = ask_patient_tool(patient_case, patient_responses, question_count)
            
            new_messages = messages + [
                SystemMessage(content="[Diagnostic Agent] Pose une question au patient."),
                AIMessage(content=f"Question {question_count + 1}/5: {question}")
            ]
            
            return {
                **state,
                "messages": new_messages,
                "question_count": question_count + 1,
            }
        
        if question_count >= 5 and not state.get("diagnostic_summary"):
            diagnostic_summary = self._generate_summary(patient_case, patient_responses)
            interim_care = recommend_interim_care_tool(diagnostic_summary)
            
            new_messages = messages + [
                SystemMessage(content="[Diagnostic Agent] Synthese clinique preliminaire generee."),
                AIMessage(content=f"Synthese clinique preliminaire:\n{diagnostic_summary}\n\nRecommandation intermediaire:\n{interim_care}")
            ]
            
            return {
                **state,
                "messages": new_messages,
                "diagnostic_summary": diagnostic_summary,
                "interim_care": interim_care,
            }
        
        return state
    
    def _generate_summary(self, patient_case: str, responses: list) -> str:
        context = f"Cas initial: {patient_case}\n\nReponses patient:\n"
        for i, resp in enumerate(responses, 1):
            context += f"{i}. {resp.get('question', '')}\n   -> {resp.get('answer', '')}\n"
        
        prompt = f"""En tant qu'assistant medical academique (NON un dispositif medical), analysez les informations suivantes et produisez une synthese clinique preliminaire PRUDENTE.

{context}

Produisez une synthese structuree avec:
1. Points cles rapportes
2. Elements a surveiller
3. Orientation preliminaire (sans diagnostic definitif)

Ce systeme ne remplace pas une consultation medicale."""
        
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content
