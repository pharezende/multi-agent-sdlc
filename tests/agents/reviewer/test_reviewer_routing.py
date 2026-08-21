from langchain_core.messages import AIMessage

from multi_agent_sdlc.agents.reviewer.routing import route_after_reviewer
from multi_agent_sdlc.workflow.models import ReviewStatus
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_reviewer_routes_approved_to_deployer(
    dev_state: DevState,
) -> None:
    dev_state["review_status"] = ReviewStatus.PASSED
    dev_state["reviewer_messages"] = [
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

    assert route_after_reviewer(dev_state) == "deployer"


def test_route_after_reviewer_routes_changes_required_to_coder_repair(
    dev_state: DevState,
) -> None:
    dev_state["review_status"] = ReviewStatus.REPAIR_REQUIRED
    dev_state["reviewer_messages"] = [
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

    assert route_after_reviewer(dev_state) == "prepare_coder_repair"


def test_route_after_reviewer_routes_blocked_to_end(dev_state: DevState) -> None:
    dev_state["review_status"] = ReviewStatus.BLOCKED
    dev_state["reviewer_messages"] = [
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

    assert route_after_reviewer(dev_state) == "__end__"


def test_route_after_reviewer_routes_tool_call_to_reviewer_tools(
    dev_state: DevState,
) -> None:
    dev_state["review_status"] = None
    dev_state["reviewer_messages"] = [
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

    assert route_after_reviewer(dev_state) == "reviewer_tools"


def test_route_after_reviewer_routes_without_tool_call_back_to_reviewer(
    dev_state: DevState,
) -> None:
    dev_state["review_status"] = None
    dev_state["reviewer_messages"] = [
        AIMessage(
            content="Continue reviewing the implementation.",
        )
    ]

    assert route_after_reviewer(dev_state) == "reviewer"
