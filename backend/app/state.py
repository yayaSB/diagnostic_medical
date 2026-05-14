from typing import Annotated, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class MedicalState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    next: Literal["diagnostic_agent", "physician_review", "report_agent", "FINISH"]
    thread_id: str
    initial_case: str
    questions: list[str]
    patient_answers: list[str]
    question_count: int
    interim_care: str
    diagnostic_summary: str
    physician_treatment: str
    physician_notes: str
    final_report: str