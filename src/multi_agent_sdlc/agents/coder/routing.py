from multi_agent_sdlc.workflow.state import DevState
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.agents.coder.node import MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
from typing import Literal

from langchain_core.messages import AIMessage


def route_after_coder(
    state: DevState,
) -> Literal["coder_tools", "prepare_tester", "coder", "__end__"]:
    coder_status = state.get("coder_status")
    if coder_status is DevelopmentStatus.COMPLETED:
        return "prepare_tester"
    if (
        coder_status is DevelopmentStatus.FAILED
        and state["coder_invalid_response_count"]
        >= MAX_CONSECUTIVE_CODER_INVALID_RESPONSES
    ):
        print(
            f"Coder produced {MAX_CONSECUTIVE_CODER_INVALID_RESPONSES} consecutive invalid "
            "responses. Stopping workflow execution."
        )
        return "__end__"  # future
    # if coder_status is CoderStatus.BLOCKED:
    #     return "human_intervention"  # future

    messages = state.get("coder_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "coder_tools"

    return "coder"
