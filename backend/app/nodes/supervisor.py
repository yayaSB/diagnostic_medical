from typing import Literal
from langchain_core.messages import SystemMessage
from backend.app.state import MedicalState

class SupervisorNode:
    def __init__(self):
        pass
    
    def __call__(self, state: MedicalState) -> MedicalState:
        messages = state.get("messages", [])
        question_count = state.get("question_count", 0)
        diagnostic_summary = state.get("diagnostic_summary", "")
        physician_treatment = state.get("physician_treatment", "")
        final_report = state.get("final_report", "")
        
        if not diagnostic_summary and question_count < 5:
            next_step = "diagnostic_agent"
        elif diagnostic_summary and not physician_treatment:
            next_step = "physician_review"
        elif physician_treatment and not final_report:
            next_step = "report_agent"
        else:
            next_step = "FINISH"
        
        return {
            **state,
            "next": next_step,
            "messages": messages + [SystemMessage(content=f"[Supervisor] Prochaine etape: {next_step}")]
        }
    
    def route(self, state: MedicalState) -> Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]:
        return state.get("next", "FINISH")
