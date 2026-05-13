from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.state import MedicalState
from backend.app.nodes.supervisor import SupervisorNode
from backend.app.nodes.diagnostic_agent import DiagnosticAgentNode
from backend.app.nodes.physician_review import PhysicianReviewNode
from backend.app.nodes.report_agent import ReportAgentNode

def create_medical_graph():
    supervisor = SupervisorNode()
    diagnostic_agent = DiagnosticAgentNode()
    physician_review = PhysicianReviewNode()
    report_agent = ReportAgentNode()
    
    workflow = StateGraph(MedicalState)
    
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("diagnostic_agent", diagnostic_agent)
    workflow.add_node("physician_review", physician_review)
    workflow.add_node("report_agent", report_agent)
    
    workflow.set_entry_point("supervisor")
    
    workflow.add_conditional_edges(
        "supervisor",
        supervisor.route,
        {
            "diagnostic_agent": "diagnostic_agent",
            "physician_review": "physician_review",
            "report_agent": "report_agent",
            "FINISH": END
        }
    )
    
    workflow.add_edge("diagnostic_agent", "supervisor")
    workflow.add_edge("physician_review", "supervisor")
    workflow.add_edge("report_agent", "supervisor")
    
    checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph

medical_graph = create_medical_graph()