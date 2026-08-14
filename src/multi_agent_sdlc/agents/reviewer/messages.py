import json
from multi_agent_sdlc.agents.reviewer.prompt import REVIEWER_REREVIEW_PROMPT_TEMPLATE
from multi_agent_sdlc.agents.reviewer.prompt import REVIEWER_INITIAL_PROMPT_TEMPLATE
from multi_agent_sdlc.agents.reviewer.prompt import REVIEWER_SYSTEM_RULES
from langchain_core.messages import BaseMessage
from multi_agent_sdlc.agents.reviewer.context import build_reviewer_context
from multi_agent_sdlc.workflow.state import DevState


def build_reviewer_initial_messages(state: DevState) -> list[BaseMessage]:
    reviewer_context = build_reviewer_context(state)

    prompt = REVIEWER_INITIAL_PROMPT_TEMPLATE.invoke(
        {
            "reviewer_rules": REVIEWER_SYSTEM_RULES,
            "reviewer_context": json.dumps(reviewer_context, indent=2),
        }
    )

    return prompt.to_messages()


def build_reviewer_rereview_messages(state: DevState) -> list[BaseMessage]:
    reviewer_context = build_reviewer_context(state)

    prompt = REVIEWER_REREVIEW_PROMPT_TEMPLATE.invoke(
        {
            "reviewer_context": json.dumps(reviewer_context, indent=2),
        }
    )

    return prompt.to_messages()
