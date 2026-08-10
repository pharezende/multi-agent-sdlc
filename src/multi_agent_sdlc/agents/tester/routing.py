from typing import Literal

from langchain_core.messages import AIMessage

from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.state import DevState


def route_after_tester(
    state: DevState,
) -> Literal[
    "prepare_coder_repair",
    "tester_tools",
    "reviewer",
    "tester",
]:
    verification_status = state.get("verification_status")

    if verification_status == VerificationStatus.REPAIR_REQUIRED:
        return "prepare_coder_repair"

    if verification_status == VerificationStatus.PASSED:
        return "reviewer"

    # if verification_status is TesterStatus.BLOCKED:
    #     return "human_intervention"  # future

    messages = state.get("tester_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tester_tools"

    return "tester"
