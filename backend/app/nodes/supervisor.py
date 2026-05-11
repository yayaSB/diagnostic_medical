from app.state import MedicalState


def supervisor(state: MedicalState) -> MedicalState:
    if not state.get("diagnostic_summary"):
        return {"next": "diagnostic_agent"}
    if not state.get("physician_treatment"):
        return {"next": "physician_review"}
    if not state.get("final_report"):
        return {"next": "report_agent"}
    return {"next": "FINISH"}
