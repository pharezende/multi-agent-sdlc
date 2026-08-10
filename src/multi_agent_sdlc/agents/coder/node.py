from langchain_core.messages import AIMessage, HumanMessage

from multi_agent_sdlc.agents.coder.llm import coder_llm
from multi_agent_sdlc.agents.coder.models import CoderCycle, CoderSummary
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_INVALID_RESPONSE_FEEDBACK,
    CODER_SUBMIT_SUMMARY_WITH_OTHER_TOOLS_FEEDBACK,
)
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.workflow.state import DevState

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

        return _process_coder_summary_call(state, response)

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
            "development_status": DevelopmentStatus.FAILED,
        }

    return {
        "coder_messages": [
            response,
            HumanMessage(content=feedback),
        ],
        "coder_invalid_response_count": invalid_count,
    }


def _process_coder_summary_call(
    state: DevState,
    response: AIMessage,
) -> dict[str, object]:
    tool_call = response.tool_calls[0]

    coder_summary = CoderSummary.model_validate(tool_call["args"]["summary"])

    coder_summary_history = state["coder_summary_history"]

    coder_cycle = CoderCycle(
        cycle_number=(
            coder_summary_history[-1].cycle_number + 1 if coder_summary_history else 1
        ),
        coder_summary=coder_summary,
    )

    return {
        "coder_messages": [response],
        "current_coder_summary": coder_summary,
        "coder_summary_history": [coder_cycle],
        "development_status": DevelopmentStatus.COMPLETED,
        "coder_invalid_response_count": 0,
    }
