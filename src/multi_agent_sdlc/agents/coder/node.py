from multi_agent_sdlc.models import CoderMode
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

    coder_messages = state.get("coder_messages", [])
    coder_mode = state.get("coder_mode", CoderMode.IMPLEMENTATION)
    current_tester_summary = state.get("current_tester_summary")

    if not coder_messages:
        return _initialize_coder_conversation(state)

    if coder_mode is CoderMode.REPAIR:
        coder_messages.append(
            HumanMessage(
                content=(
                    "The Tester found production defects requiring repair.\n\n"
                    f"{current_tester_summary.model_dump_json(indent=2)}"
                )
            )
        )

    response = coder_llm.invoke(coder_messages)

    if response.tool_calls:
        if response.tool_calls[0]["name"] == "submit_coder_summary":
            return _process_coder_summary_call(state, response)

    return {
        "coder_messages": [response],
    }


def _initialize_coder_conversation(state: DevState) -> dict:
    prompt_value = CODER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_rules": CODER_SYSTEM_RULES,
            "coder_context": json.dumps(
                build_coder_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    initial_messages = prompt_value.to_messages()
    response = coder_llm.invoke(initial_messages)

    return {
        "coder_messages": [
            *initial_messages,
            response,
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

    implementation_cycle = ImplementationCycle(
        cycle_number=len(history) + 1,
        mode=state.get("coder_mode", CoderMode.IMPLEMENTATION),
        coder_summary=coder_summary,
    )

    return {
        "coder_messages": [response],
        "current_coder_summary": coder_summary,
        "coder_summary_history": [implementation_cycle],
    }
