from multi_agent_sdlc.agents.coder.prompt import (
    CODER_CHAT_PROMPT_TEMPLATE,
    CODER_SYSTEM_RULES,
)
from multi_agent_sdlc.models import CoderSummary
from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.agents.coder.context import build_coder_context
from langchain_core.language_models.chat_models import BaseChatModel
import json


def create_coder_node(
    llm_with_tools: BaseChatModel,
):

    def coder_node(state: DevState) -> dict:

        coder_messages = state.get("coder_messages", [])

        if not coder_messages:

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
            response = llm_with_tools.invoke(initial_messages)

            return {
                "coder_messages": [
                    *initial_messages,
                    response,
                ],
            }

        response = llm_with_tools.invoke(coder_messages)

        print("CONTENT:")
        print(repr(response.content))

        print("\nTOOL CALLS:")
        print(response.tool_calls)

        print("\nINVALID TOOL CALLS:")
        print(getattr(response, "invalid_tool_calls", None))

        if response.tool_calls:
            tool_call = response.tool_calls[0]
            if tool_call["name"] == "submit_coder_summary":
                if len(response.tool_calls) != 1:
                    raise ValueError("`submit_coder_summary` must be called alone.")

                coder_summary = CoderSummary.model_validate(
                    tool_call["args"]["summary"]
                )

                return {
                    "coder_messages": [response],
                    "coder_summary": coder_summary,
                }

        return {
            "coder_messages": [response],
        }

        # summary = CoderSummary.model_validate_json(response.content)

        # return {
        #     "coder_summary": summary,
        # }

        # payload = response.tool_calls[0]["args"]

        # coder_summary = CoderSummary.model_validate(
        #     payload["summary"]
        # )

    return coder_node
