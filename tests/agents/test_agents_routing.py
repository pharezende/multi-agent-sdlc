from multi_agent_sdlc.agents.reviewer.routing import route_after_reviewer
from multi_agent_sdlc.workflow.models import ReviewStatus
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

    assert route_after_tester(state) == "prepare_reviewer"


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


def test_route_after_reviewer_routes_approved_to_end() -> None:
    state: DevState = build_initial_state("test request")
    state["review_status"] = ReviewStatus.PASSED
    state["reviewer_messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "submit_reviewer_summary",
                    "args": {},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
    ]

    result = route_after_reviewer(state)

    assert result == "__end__"


def test_route_after_reviewer_routes_changes_required_to_coder_repair() -> None:
    state: DevState = build_initial_state("test request")
    state["review_status"] = ReviewStatus.REPAIR_REQUIRED
    state["reviewer_messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "submit_reviewer_summary",
                    "args": {},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
    ]

    result = route_after_reviewer(state)

    assert result == "prepare_coder_repair"


def test_route_after_reviewer_routes_blocked_to_end() -> None:
    state: DevState = build_initial_state("test request")
    state["review_status"] = ReviewStatus.BLOCKED
    state["reviewer_messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "submit_reviewer_summary",
                    "args": {},
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
    ]

    result = route_after_reviewer(state)

    assert result == "__end__"


def test_route_after_reviewer_routes_tool_call_to_reviewer_tools() -> None:
    state: DevState = build_initial_state("test request")
    state["review_status"] = None
    state["reviewer_messages"] = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "read_file",
                    "args": {
                        "path": "src/main.py",
                    },
                    "id": "call-1",
                    "type": "tool_call",
                }
            ],
        )
    ]

    result = route_after_reviewer(state)

    assert result == "reviewer_tools"


def test_route_after_reviewer_routes_without_tool_call_back_to_reviewer() -> None:
    state: DevState = build_initial_state("test request")
    state["review_status"] = None
    state["reviewer_messages"] = [
        AIMessage(
            content="Continue reviewing the implementation.",
        )
    ]

    result = route_after_reviewer(state)

    assert result == "reviewer"
