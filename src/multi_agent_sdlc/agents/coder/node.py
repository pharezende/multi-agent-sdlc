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

    if not coder_messages:

        return _initialize_coder_conversation(state)

    response = coder_llm.invoke(coder_messages)

    if response.tool_calls:
        if response.tool_calls[0]["name"] == "submit_coder_summary":
            return _process_coder_summary_call(response)

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
