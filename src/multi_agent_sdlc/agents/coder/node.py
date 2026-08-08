from multi_agent_sdlc.agents.coder.prompt import (
    CODER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
    CODER_INVALID_RESPONSE_FEEDBACK,
)
from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.coder.model import coder_llm
from multi_agent_sdlc.models import CoderStatus, CoderSummary
from multi_agent_sdlc.state import DevState

MAX_CONSECUTIVE_CODER_INVALID_RESPONSES = 3


def coder_node(state: DevState) -> dict[str, object]:
    coder_messages = state["coder_messages"]

    if not coder_messages:
        raise ValueError("Coder conversation has not been initialized.")

    response = coder_llm.invoke(coder_messages)

    if not response.tool_calls:
        return _handle_invalid_coder_response(
            state, response, feedback=CODER_INVALID_RESPONSE_FEEDBACK
        )

    has_submit_call = any(
        tool_call["name"] == "submit_coder_summary" for tool_call in response.tool_calls
    )

    if has_submit_call:
        if len(response.tool_calls) > 1:
            return _handle_invalid_coder_response(
                state,
                response,
                feedback=CODER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
            )

        return _process_coder_summary_call(response)

    return {
        "coder_messages": [response],
        "coder_invalid_response_count": 0,
    }


def _handle_invalid_coder_response(
    state: DevState,
    response: AIMessage,
    feedback: str,
) -> dict[str, object]:
    invalid_count = state["coder_invalid_response_count"] + 1

    if invalid_count >= MAX_CONSECUTIVE_CODER_INVALID_RESPONSES:
        return {
            "coder_messages": [response],
            "coder_invalid_response_count": invalid_count,
            "coder_status": CoderStatus.FAILED,
        }

    return {
        "coder_messages": [
            response,
            HumanMessage(content=feedback),
        ],
        "coder_invalid_response_count": invalid_count,
    }


def _process_coder_summary_call(
    response: AIMessage,
) -> dict[str, object]:
    tool_call = response.tool_calls[0]

    coder_summary = CoderSummary.model_validate(tool_call["args"]["summary"])

    return {
        "coder_messages": [response],
        "current_coder_summary": coder_summary,
        "coder_status": CoderStatus.COMPLETED,
    }
