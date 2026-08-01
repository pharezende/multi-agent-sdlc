from multi_agent_sdlc.state import DevState
from langchain_core.messages import AIMessage
from typing import Literal


def route_after_tester(
    state: DevState,
) -> Literal["coder", "tester_tools", "reviewer"]:
    messages = state.get("coder_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tester_tools"

    summary = state["tester_summary"]
    if summary.coder_repair_requests:
        return "coder"

    return "reviewer"
