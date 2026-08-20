from typing import Literal

from langchain_core.messages import AIMessage

from multi_agent_sdlc.workflow.models import ReviewStatus
from multi_agent_sdlc.workflow.state import DevState


def route_after_reviewer(
    state: DevState,
) -> Literal[
    "deployer", "prepare_coder_repair", "reviewer", "reviewer_tools", "__end__"
]:

    review_status = state.get("review_status")

    if review_status == ReviewStatus.PASSED:
        return "deployer"

    if review_status == ReviewStatus.REPAIR_REQUIRED:
        return "prepare_coder_repair"

    if review_status == ReviewStatus.BLOCKED:
        return "__end__"

    last_message = state["reviewer_messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "reviewer_tools"

    return "reviewer"
