from typing import Literal

from langchain_core.messages import AIMessage

from multi_agent_sdlc.workflow.models import VerificationStatus
from multi_agent_sdlc.workflow.state import DevState


def route_after_tester(
    state: DevState,
) -> Literal[
    "tester",
    "tester_tools",
    "prepare_coder_repair",
    "prepare_reviewer",
    "human_verification_block_review",
]:
    verification_status = state.get("verification_status")

    if verification_status == VerificationStatus.REPAIR_REQUIRED:
        return "prepare_coder_repair"

    if verification_status == VerificationStatus.PASSED:
        return "prepare_reviewer"

    if verification_status == VerificationStatus.BLOCKED:
        return "human_verification_block_review"

    last_message = state["tester_messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tester_tools"

    return "tester"
