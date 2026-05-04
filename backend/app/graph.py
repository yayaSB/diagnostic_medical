from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.nodes.diagnostic_agent import diagnostic_agent
from app.nodes.physician_review import physician_review
from app.nodes.report_agent import report_agent
from app.nodes.supervisor import supervisor
from app.state import MedicalState


def route_next(state: MedicalState) -> str:
    return state["next"]


def build_graph():
    builder = StateGraph(MedicalState)
    builder.add_node("supervisor", supervisor)
    builder.add_node("diagnostic_agent", diagnostic_agent)
    builder.add_node("physician_review", physician_review)
    builder.add_node("report_agent", report_agent)

    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges(
        "supervisor",
        route_next,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END,
        },
    )
    builder.add_edge("diagnostic_agent", "supervisor")
    builder.add_edge("physician_review", "supervisor")
    builder.add_edge("report_agent", "supervisor")

    return builder.compile(checkpointer=MemorySaver())


graph = build_graph()
