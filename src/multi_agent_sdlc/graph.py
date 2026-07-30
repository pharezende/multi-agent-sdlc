from langgraph.types import TimeoutPolicy
from multi_agent_sdlc.agents.planner.node import create_planner_node
from multi_agent_sdlc.agents.coder.node import create_coder_node
from multi_agent_sdlc.agents.planner.model import planner_llm
from multi_agent_sdlc.agents.coder.routing import route_after_coder
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS
from multi_agent_sdlc.agents.coder.model import coder_llm
from multi_agent_sdlc.nodes import finalize_coder
from langgraph.graph import END, START, StateGraph
from .state import DevState
from langgraph.prebuilt import ToolNode


def build_graph():

    # llm_free = create_llm()
    # llm_paid = coder_llm
    planner_node = create_planner_node(planner_llm)
    coder_node = create_coder_node(coder_llm)
    coder_tool_node = ToolNode(
        CODER_TOOLS,
        messages_key="coder_messages",
        handle_tool_errors=True,
    )

    builder = StateGraph(DevState)
    builder.add_node("planner", planner_node)
    builder.add_node("coder", coder_node)
    builder.add_node("coder_tools", coder_tool_node)
    builder.add_node("finalize_coder", finalize_coder)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "coder")
    builder.add_conditional_edges(
        "coder",
        route_after_coder,
        {
            "coder_tools": "coder_tools",
            "finalize_coder": "finalize_coder",
        },
    )

    builder.add_edge("coder_tools", "coder")

    builder.add_edge("finalize_coder", END)

    return builder.compile()
