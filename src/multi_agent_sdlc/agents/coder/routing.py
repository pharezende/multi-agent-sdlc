from typing import Literal

from langchain_core.messages import AIMessage

from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.state import DevState


def route_after_coder(
    state: DevState,
) -> Literal["coder_tools", "prepare_tester", "coder"]:
    coder_status = state.get("coder_status")
    if coder_status is CoderStatus.COMPLETED:
        return "prepare_tester"
    # if coder_status in {CoderStatus.BLOCKED, CoderStatus.FAILED}:
    #     return "human_intervention"  # future

    messages = state.get("coder_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "coder_tools"

    return "coder"
