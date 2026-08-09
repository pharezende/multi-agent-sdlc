from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.state import DevState
from typing import Literal

from langchain_core.messages import AIMessage


def route_after_tester(
    state: DevState,
) -> Literal[
    "prepare_coder_repair",
    "tester_tools",
    "reviewer",
    "tester",
]:
    tester_status = state.get("tester_status")

    if tester_status == VerificationStatus.REPAIR_REQUIRED:
        return "prepare_coder_repair"

    if tester_status == VerificationStatus.PASSED:
        return "reviewer"

    # if tester_status is TesterStatus.BLOCKED:
    #     return "human_intervention"  # future

    messages = state.get("tester_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tester_tools"

    return "tester"
