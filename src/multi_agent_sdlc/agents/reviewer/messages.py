import json

from langchain_core.messages import BaseMessage

from multi_agent_sdlc.agents.reviewer.context import build_reviewer_context
from multi_agent_sdlc.agents.reviewer.prompt import (
    REVIEWER_INITIAL_OVERRIDE_CHAT_PROMPT_TEMPLATE,
    REVIEWER_INITIAL_PROMPT_TEMPLATE,
    REVIEWER_REREVIEW_OVERRIDE_CHAT_PROMPT_TEMPLATE,
    REVIEWER_REREVIEW_PROMPT_TEMPLATE,
    REVIEWER_SYSTEM_RULES,
)
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


def build_reviewer_initial_override_messages(
    state: DevState,
) -> list[BaseMessage]:
    verification_block_review = state["verification_block_review"]

    if verification_block_review is None:
        raise ValueError(
            "Verification block review is required for an overridden " "initial review."
        )

    prompt_value = REVIEWER_INITIAL_OVERRIDE_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "reviewer_rules": REVIEWER_SYSTEM_RULES,
            "reviewer_context": json.dumps(
                build_reviewer_context(state),
                indent=2,
                ensure_ascii=False,
            ),
            "verification_block_review": (
                verification_block_review.model_dump_json(indent=2)
            ),
        }
    )

    return prompt_value.to_messages()


def build_reviewer_rereview_override_messages(
    state: DevState,
) -> list[BaseMessage]:
    reviewer_history = state["reviewer_summary_history"]

    if not reviewer_history:
        raise ValueError("Reviewer history is required for an overridden re-review.")

    tester_summary = state["current_tester_summary"]

    if tester_summary is None:
        raise ValueError(
            "Current Tester summary is required for an overridden re-review."
        )

    verification_block_review = state["verification_block_review"]

    if verification_block_review is None:
        raise ValueError(
            "Verification block review is required for an overridden re-review."
        )

    previous_reviewer_summary = reviewer_history[-1].reviewer_summary

    prompt_value = REVIEWER_REREVIEW_OVERRIDE_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "previous_reviewer_summary": (
                previous_reviewer_summary.model_dump_json(indent=2)
            ),
            "tester_summary": tester_summary.model_dump_json(indent=2),
            "verification_block_review": (
                verification_block_review.model_dump_json(indent=2)
            ),
        }
    )

    return prompt_value.to_messages()
