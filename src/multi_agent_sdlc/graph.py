from langgraph.graph import END, START, StateGraph
from .config import create_llm
from .nodes import create_planner_node, create_coder_node
from .state import DevState


def build_graph():
    llm = create_llm()
    planner_node = create_planner_node(llm)
    coder_node = create_coder_node(llm)

    builder = StateGraph(DevState)
    builder.add_node("plan", planner_node)
    builder.add_node("code", coder_node)

    builder.add_edge(START, "plan")
    builder.add_edge("plan", "code")
    builder.add_edge("code", END)

    return builder.compile()
