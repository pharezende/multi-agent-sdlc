import json

from langchain_core.messages import BaseMessage, HumanMessage

from multi_agent_sdlc.agents.tester.context import (
    build_tester_context,
    build_tester_retest_context,
)
from multi_agent_sdlc.agents.tester.prompt import (
    TESTER_CHAT_PROMPT_TEMPLATE,
    TESTER_RETEST_HUMAN_PROMPT,
    TESTER_SYSTEM_RULES,
)
from multi_agent_sdlc.state import DevState


def build_tester_initial_messages(
    state: DevState,
) -> list[BaseMessage]:
    prompt_value = TESTER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "tester_rules": TESTER_SYSTEM_RULES,
            "tester_execution_input": json.dumps(
                build_tester_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return prompt_value.to_messages()


def build_tester_retest_messages(
    state: DevState,
) -> HumanMessage:
    return HumanMessage(
        content=TESTER_RETEST_HUMAN_PROMPT.format(
            tester_retest_input=json.dumps(
                build_tester_retest_context(state),
                indent=2,
                ensure_ascii=False,
            )
        )
    )
