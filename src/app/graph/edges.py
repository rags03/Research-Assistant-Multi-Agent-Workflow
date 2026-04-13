from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from src.app.agents.intake_agent import ask_intake_question, record_intake_answer
from src.app.agents.retrieval_agent import retrieve_papers
from src.app.agents.library_agent import save_papers
from src.app.graph.state import ResearchState

def route_after_intake_ask(state: ResearchState) -> str:
    if state.get("intake_complete"):
        return "retrieve"
    return "record_intake"

def route_after_retrieval(state: ResearchState) -> str:
    if state.get("selected_paper_ids") is not None:
        return "save"
    return "end"

def build_graph():
    graph = StateGraph(ResearchState)

    # Nodes
    graph.add_node("ask_intake", ask_intake_question)
    graph.add_node("record_intake", record_intake_answer)
    graph.add_node("retrieve", retrieve_papers)
    graph.add_node("save", save_papers)

    # Edges
    graph.add_edge(START, "ask_intake")
    graph.add_conditional_edges("ask_intake", route_after_intake_ask, {
        "record_intake": "record_intake",
        "retrieve": "retrieve"
    })
    graph.add_edge("record_intake", "ask_intake")
    graph.add_conditional_edges("retrieve", route_after_retrieval, {
        "save": "save",
        "end": END
    })
    graph.add_edge("save", END)

    memory = MemorySaver()
    return graph.compile(checkpointer=memory, interrupt_before=["record_intake"])

if __name__ == "__main__":
    g = build_graph()
    print("Graph compiled successfully")