from multi_agent_sdlc.nodes import finalize_coder
from .nodes import route_after_coder
from langgraph.graph import END, START, StateGraph
from .config import create_llm
from .nodes import create_planner_node, create_coder_node
from .state import DevState
from langgraph.prebuilt import ToolNode
from .tools.commands import run_command
from .tools.filesystem import (
    create_directory,
    list_files,
    read_file,
    write_file,
)


def build_graph():
    coder_tools = [
        list_files,
        read_file,
        write_file,
        create_directory,
        run_command,
    ]

    llm = create_llm()
    planner_node = create_planner_node(llm)
    coder_node = create_coder_node(llm, tools=coder_tools)
    coder_tool_node = ToolNode(
        coder_tools,
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
