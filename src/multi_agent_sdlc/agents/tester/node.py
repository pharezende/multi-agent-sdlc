from multi_agent_sdlc.agents.tester.context import build_tester_context
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_CHAT_PROMPT_TEMPLATE,
    TESTER_SYSTEM_RULES,
)
from langchain_core.messages import AIMessage
from multi_agent_sdlc.agents.coder.model import coder_llm
from multi_agent_sdlc.models import CoderSummary
from multi_agent_sdlc.state import DevState
import json


def tester_node(state: DevState) -> dict:

    tester_messages = state.get("tester_messages", [])

    if not tester_messages:

        return _initialize_tester_conversation(state)

    response = coder_llm.invoke(tester_messages)

    if response.tool_calls:
        if response.tool_calls[0]["name"] == "submit_coder_summary":
            return _process_coder_summary_call(response)

    return {
        "tester_messages": [response],
    }


def _initialize_tester_conversation(state: DevState) -> dict:
    prompt_value = TESTER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "tester_rules": TESTER_SYSTEM_RULES,
            "tester_context": json.dumps(
                build_tester_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    initial_messages = prompt_value.to_messages()
    response = coder_llm.invoke(initial_messages)

    return {
        "tester_messages": [
            *initial_messages,
            response,
        ],
    }


def _process_coder_summary_call(response: AIMessage) -> dict:
    if len(response.tool_calls) != 1:
        raise ValueError("`submit_coder_summary` must be called alone.")

    coder_summary = CoderSummary.model_validate(
        response.tool_calls[0]["args"]["summary"]
    )

    return {
        "coder_messages": [response],
        "coder_summary": coder_summary,
    }
