from multi_agent_sdlc.tools.commands import CODER_TOOLS
from multi_agent_sdlc.nodes import finalize_coder
from .nodes import route_after_coder
from langgraph.graph import END, START, StateGraph
from .config import create_llm
from .nodes import create_planner_node, create_coder_node
from .state import DevState
from langgraph.prebuilt import ToolNode


def build_graph():

    llm = create_llm()
    planner_node = create_planner_node(llm)
    coder_node = create_coder_node(llm, tools=CODER_TOOLS)
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
