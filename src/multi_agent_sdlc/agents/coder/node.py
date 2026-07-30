from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.agents.coder.context import build_coder_context
from multi_agent_sdlc.prompts.coder import CODER_PROMPT
from langchain_core.language_models.chat_models import BaseChatModel
import json


def create_coder_node(
    llm_with_tools: BaseChatModel,
):

    def coder_node(state: DevState) -> dict:

        coder_messages = state.get("coder_messages", [])

        if not coder_messages:
            initial_messages = CODER_PROMPT.format_messages(
                coder_context=json.dumps(
                    build_coder_context(state),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            response = llm_with_tools.invoke(initial_messages)

            return {
                "coder_messages": [
                    *initial_messages,
                    response,
                ],
            }

        response = llm_with_tools.invoke(coder_messages)

        return {
            "coder_messages": [response],
        }

    return coder_node
