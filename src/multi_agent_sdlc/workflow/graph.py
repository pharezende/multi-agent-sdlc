from multi_agent_sdlc.agents.planner.llm import create_planner_llm
from multi_agent_sdlc.agents.coder.llm import create_coder_llm
from functools import partial
from multi_agent_sdlc.agents.tester.llm import create_tester_llm
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import ToolNode

from multi_agent_sdlc.agents.coder.node import coder_node
from multi_agent_sdlc.agents.coder.routing import route_after_coder
from multi_agent_sdlc.agents.planner.node import planner_node
from multi_agent_sdlc.agents.reviewer.reviewer import reviewer_node
from multi_agent_sdlc.agents.tester.node import tester_node
from multi_agent_sdlc.agents.tester.routing import route_after_tester
from multi_agent_sdlc.human_in_the_loop.plan_review import human_plan_review_node
from multi_agent_sdlc.human_in_the_loop.routing import route_after_plan_review
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS
from multi_agent_sdlc.tools.tester.registry import TESTER_TOOLS

from .state import DevState
from .transitions import (
    prepare_coder_implementation_node,
    prepare_coder_repair_node,
    prepare_plan_review_node,
    prepare_planner_revision_node,
    prepare_tester_node,
)


def generate_diagram(graph: CompiledStateGraph) -> None:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("multi_agent_sdlc_workflow.png", "wb") as file:
        file.write(png_data)


def build_graph(checkpointer: BaseCheckpointSaver):

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
    planner_llm = create_planner_llm()
    planner_action = partial(planner_node, planner_llm=planner_llm)
    coder_llm = create_coder_llm()
    coder_action = partial(coder_node, coder_llm=coder_llm)
    tester_llm = create_tester_llm()
    tester_action = partial(tester_node, tester_llm=tester_llm)
    builder.add_node("planner", planner_action)
    builder.add_node("prepare_plan_review", prepare_plan_review_node)
    builder.add_node("human_plan_review", human_plan_review_node)
    builder.add_node("prepare_planner_revision", prepare_planner_revision_node)
    builder.add_node("prepare_coder_implementation", prepare_coder_implementation_node)
    builder.add_node("coder", coder_action)
    builder.add_node("coder_tools", coder_tool_node)
    builder.add_node("prepare_tester", prepare_tester_node)
    builder.add_node("tester", tester_action)
    builder.add_node("tester_tools", tester_tool_node)
    builder.add_node("prepare_coder_repair", prepare_coder_repair_node)
    builder.add_node("reviewer", reviewer_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "prepare_plan_review")
    builder.add_edge("prepare_plan_review", "human_plan_review")
    builder.add_conditional_edges(
        "human_plan_review",
        route_after_plan_review,
        {
            "prepare_coder_implementation": "prepare_coder_implementation",
            "prepare_planner_revision": "prepare_planner_revision",
            "__end__": "__end__",
        },
    )
    builder.add_edge("prepare_planner_revision", "planner")
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

    return builder.compile(
        checkpointer=checkpointer,
    )
