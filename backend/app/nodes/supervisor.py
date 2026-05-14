from backend.app.state import MedicalState


class SupervisorNode:
    def __call__(self, state: MedicalState) -> MedicalState:
        count = state.get("question_count", 0)
        has_summary = bool(state.get("diagnostic_summary"))
        has_treatment = bool(state.get("physician_treatment"))
        has_report = bool(state.get("final_report"))
        
        # If we have a final report, we're done
        if has_report:
            state["next"] = "FINISH"
        # If we have a diagnostic summary but no physician treatment, go to physician review
        elif has_summary and not has_treatment:
            state["next"] = "physician_review"
        # If we have physician treatment but no report, go to report agent
        elif has_treatment and not has_report:
            state["next"] = "report_agent"
        # Otherwise, keep asking questions (diagnostic_agent handles the count)
        else:
            state["next"] = "diagnostic_agent"
        
        return state

    def route(self, state: MedicalState) -> str:
        return state.get("next", "FINISH")