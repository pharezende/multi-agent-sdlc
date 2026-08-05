from multi_agent_sdlc.models import TesterStatus
from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.models import ImplementationCycle
from langchain_core.messages import HumanMessage
from langchain_core.messages import AIMessage
from multi_agent_sdlc.agents.coder.model import coder_llm
from multi_agent_sdlc.models import CoderSummary
from multi_agent_sdlc.state import DevState


def coder_node(state: DevState) -> dict[str, object]:
    coder_messages = state["coder_messages"]

    if not coder_messages:
        raise ValueError("Coder conversation has not been initialized.")

    response = coder_llm.invoke(coder_messages)

    if response.tool_calls:
        submit_calls = [
            tool_call
            for tool_call in response.tool_calls
            if tool_call["name"] == "submit_coder_summary"
        ]

        if submit_calls:
            if len(response.tool_calls) != 1:
                return {
                    "coder_messages": [
                        response,
                        HumanMessage(
                            content=(
                                "`submit_coder_summary` must be called alone. "
                                "Complete any operational tool calls first, "
                                "then submit the Coder summary in a separate "
                                "response."
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
                    "Call one or more approved Coder operational tools, "
                    "or call `submit_coder_summary` alone."
                )
            ),
        ],
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
