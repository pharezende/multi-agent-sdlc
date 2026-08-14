from multi_agent_sdlc.agents.tester.routing import route_after_tester
from multi_agent_sdlc.agents.coder.node import MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
from langchain_core.messages import AIMessage
from multi_agent_sdlc.agents.coder.routing import route_after_coder
from multi_agent_sdlc.workflow.models import DevelopmentStatus, VerificationStatus
from multi_agent_sdlc.workflow.state import build_initial_state
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_coder_completed_routes_to_tester() -> None:
    state = build_initial_state("test request")
    state["development_status"] = DevelopmentStatus.COMPLETED

    assert route_after_coder(state) == "prepare_tester"


def test_route_after_coder_tool_call_routes_to_tools() -> None:
    state = build_initial_state("test request")
    state["development_status"] = DevelopmentStatus.IMPLEMENTING
    state["coder_messages"] = [
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

    assert route_after_coder(state) == "coder_tools"


def test_route_after_coder_without_tool_call_routes_to_coder():
    state: DevState = build_initial_state("test request")
    state["development_status"] = DevelopmentStatus.IMPLEMENTING
    state["coder_messages"] = [
        AIMessage(
            content="test",
        )
    ]
    assert route_after_coder(state) == "coder"


def test_route_after_coder_failed_ends():
    state: DevState = build_initial_state("test request")
    state["development_status"] = DevelopmentStatus.FAILED
    state["coder_invalid_response_count"] = MAX_CONSECUTIVE_CODER_INVALID_RESPONSES

    assert route_after_coder(state) == "__end__"


def test_route_after_tester_passed_routes_to_reviewer() -> None:
    state = build_initial_state("test request")
    state["verification_status"] = VerificationStatus.PASSED

    assert route_after_tester(state) == "reviewer"


def test_route_after_tester_repair_required_routes_to_reviewer() -> None:
    state = build_initial_state("test request")
    state["verification_status"] = VerificationStatus.REPAIR_REQUIRED

    assert route_after_tester(state) == "prepare_coder_repair"


def test_route_after_tester_tool_call_routes_to_tester_tools():
    state: DevState = build_initial_state("test request")
    state["verification_status"] = VerificationStatus.VERIFYING
    state["tester_messages"] = [
        AIMessage(
            content="test",
        )
    ]
    assert route_after_tester(state) == "tester"


def test_route_after_tester_without_tool_call_routes_to_tester():
    state: DevState = build_initial_state("test request")
    state["verification_status"] = VerificationStatus.VERIFYING
    state["tester_messages"] = [
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
    assert route_after_tester(state) == "tester_tools"
