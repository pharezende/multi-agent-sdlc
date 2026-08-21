from langchain_core.messages import AIMessage

from multi_agent_sdlc.agents.tester.routing import route_after_tester
from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_tester_passed_routes_to_reviewer(dev_state: DevState) -> None:
    dev_state["verification_status"] = VerificationStatus.PASSED

    assert route_after_tester(dev_state) == "prepare_reviewer"


def test_route_after_tester_repair_required_routes_to_reviewer(
    dev_state: DevState,
) -> None:
    dev_state["verification_status"] = VerificationStatus.REPAIR_REQUIRED

    assert route_after_tester(dev_state) == "prepare_coder_repair"


def test_route_after_tester_without_tool_call_routes_to_tester(
    dev_state: DevState,
) -> None:
    dev_state["verification_status"] = VerificationStatus.VERIFYING
    dev_state["tester_messages"] = [
        AIMessage(
            content="test",
        )
    ]

    assert route_after_tester(dev_state) == "tester"


def test_route_after_tester_tool_call_routes_to_tester_tools(
    dev_state: DevState,
) -> None:
    dev_state["verification_status"] = VerificationStatus.VERIFYING
    dev_state["tester_messages"] = [
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

    assert route_after_tester(dev_state) == "tester_tools"
