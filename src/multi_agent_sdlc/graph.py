from multi_agent_sdlc.state import DevState
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from multi_agent_sdlc.agents.coder.node import coder_node
from multi_agent_sdlc.agents.coder.routing import route_after_coder
from multi_agent_sdlc.agents.planner.node import planner_node
from multi_agent_sdlc.agents.tester.node import tester_node
from multi_agent_sdlc.agents.tester.routing import route_after_tester
from multi_agent_sdlc.reviewer import reviewer_node
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS
from multi_agent_sdlc.tools.tester.registry import TESTER_TOOLS
from multi_agent_sdlc.transitions import (
    prepare_coder_implementation_node,
    prepare_coder_repair_node,
    prepare_tester_node,
)


def build_graph():

    builder = StateGraph(DevState)
    coder_tool_node = ToolNode(
        CODER_TOOLS,
        messages_key="coder_messages",
        handle_tool_errors=True,
    )
    tester_tool_node = ToolNode(
        TESTER_TOOLS,
        messages_key="tester_messages",
        handle_tool_errors=True,
    )
    builder.add_node("planner", planner_node)
    builder.add_node("prepare_coder_implementation", prepare_coder_implementation_node)
    builder.add_node("coder", coder_node)
    builder.add_node("coder_tools", coder_tool_node)
    builder.add_node("prepare_tester", prepare_tester_node)
    builder.add_node("tester", tester_node)
    builder.add_node("tester_tools", tester_tool_node)
    builder.add_node("prepare_coder_repair", prepare_coder_repair_node)
    builder.add_node("reviewer", reviewer_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "prepare_coder_implementation")
    builder.add_edge("prepare_coder_implementation", "coder")
    builder.add_conditional_edges(
        "coder",
        route_after_coder,
        {
            "coder": "coder",
            "coder_tools": "coder_tools",
            "prepare_tester": "prepare_tester",
        },
    )
    builder.add_edge("coder_tools", "coder")
    builder.add_edge("prepare_tester", "tester")
    builder.add_conditional_edges(
        "tester",
        route_after_tester,
        {
            "tester_tools": "tester_tools",
            "reviewer": "reviewer",
            "prepare_coder_repair": "prepare_coder_repair",
            "tester": "tester",
        },
    )
    builder.add_edge("prepare_coder_repair", "coder")
    builder.add_edge("tester_tools", "tester")
    builder.add_edge("reviewer", END)

    return builder.compile()
