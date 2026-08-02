from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.state import DevState
from langchain_core.messages import AIMessage
from typing import Literal


def route_after_coder(
    state: DevState,
) -> Literal[
    "coder_tools",
    "tester",
]:
    coder_status = state.get("coder_status", CoderStatus.IMPLEMENTING)
    if coder_status is CoderStatus.COMPLETED:
        return "tester"
    if coder_status in {CoderStatus.BLOCKED, CoderStatus.FAILED}:
        raise ValueError("Future implementation")

    messages = state.get("coder_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "coder_tools"

    raise ValueError("Empty message and no tool called!")
