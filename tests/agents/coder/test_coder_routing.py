from langchain_core.messages import AIMessage

from multi_agent_sdlc.agents.coder.node import MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
from multi_agent_sdlc.agents.coder.routing import route_after_coder
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_coder_completed_routes_to_tester(dev_state: DevState) -> None:
    dev_state["development_status"] = DevelopmentStatus.COMPLETED

    assert route_after_coder(dev_state) == "prepare_tester"


def test_route_after_coder_tool_call_routes_to_tools(dev_state: DevState) -> None:
    dev_state["development_status"] = DevelopmentStatus.IMPLEMENTING
    dev_state["coder_messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "test_tool",
                    "args": {},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
    ]

    assert route_after_coder(dev_state) == "coder_tools"


def test_route_after_coder_without_tool_call_routes_to_coder(
    dev_state: DevState,
) -> None:
    dev_state["development_status"] = DevelopmentStatus.IMPLEMENTING
    dev_state["coder_messages"] = [
        AIMessage(
            content="test",
        )
    ]

    assert route_after_coder(dev_state) == "coder"


def test_route_after_coder_failed_ends(dev_state: DevState) -> None:
    dev_state["development_status"] = DevelopmentStatus.FAILED
    dev_state["coder_invalid_response_count"] = (
        MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
    )

    assert route_after_coder(dev_state) == "__end__"
