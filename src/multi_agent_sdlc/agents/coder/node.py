from multi_agent_sdlc.models import TesterStatus
from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.models import ImplementationCycle
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from multi_agent_sdlc.agents.coder.model import coder_llm
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_CHAT_PROMPT_TEMPLATE,
    CODER_SYSTEM_RULES,
)
from multi_agent_sdlc.models import CoderSummary
from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.agents.coder.context import build_coder_context
import json


def coder_node(state: DevState) -> dict:
    coder_messages = state["coder_messages"]

    if not coder_messages:
        raise ValueError("Coder conversation has not been initialized.")

    response = coder_llm.invoke(coder_messages)

    if response.tool_calls:
        first_tool_call = response.tool_calls[0]

        if first_tool_call["name"] == "submit_coder_summary":
            if len(response.tool_calls) != 1:
                return {
                    "coder_messages": [
                        response,
                        HumanMessage(
                            content=(
                                "`submit_coder_summary` must be called alone. "
                                "Correct the response and call it again."
                            )
                        ),
                    ],
                }

            return _process_coder_summary_call(
                state,
                response,
            )

        return {
            "coder_messages": [response],
        }

    return {
        "coder_messages": [
            response,
            HumanMessage(
                content=(
                    "Invalid response. Return no explanatory text. "
                    "Call exactly one approved Coder operational tool, "
                    "or call `submit_coder_summary` alone."
                )
            ),
        ],
    }


def _process_coder_summary_call(
    state: DevState,
    response: AIMessage,
) -> dict[str, object]:
    if len(response.tool_calls) != 1:
        raise ValueError("`submit_coder_summary` must be called alone.")

    tool_call = response.tool_calls[0]

    coder_summary = CoderSummary.model_validate(tool_call["args"]["summary"])

    history = state.get("coder_summary_history", [])

    coder_status = state.get("coder_status", CoderStatus.IMPLEMENTING)
    tester_status = state.get(
        "tester_status",
        TesterStatus.TESTING_PENDING,
    )

    implementation_cycle = ImplementationCycle(
        cycle_number=(history[-1].cycle_number + 1 if history else 1),
        coder_status=coder_status,
        coder_summary=coder_summary,
    )

    # Implement later
    # if coder_summary.failed_task_ids:
    #     resulting_status = CoderStatus.FAILED
    # elif coder_summary.blocked_task_ids:
    #     resulting_status = CoderStatus.BLOCKED
    resulting_status = CoderStatus.COMPLETED

    return {
        "coder_messages": [response],
        "current_coder_summary": coder_summary,
        "coder_summary_history": [implementation_cycle],
        "coder_status": resulting_status,
        "tester_status": tester_status,
    }
