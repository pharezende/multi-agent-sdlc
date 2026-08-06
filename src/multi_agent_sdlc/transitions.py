from langchain_core.messages import HumanMessage
from multi_agent_sdlc.agents.planner.prompt import (
    PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE,
)
from multi_agent_sdlc.agents.presentation.plan_formatter import format_plan
from multi_agent_sdlc.models import PlanReviewStatus
from multi_agent_sdlc.models import PreparePlanReviewUpdate
import json

from multi_agent_sdlc.agents.coder.context import (
    build_coder_context,
    build_coder_repair_context,
)
from multi_agent_sdlc.agents.coder.messages import (
    build_tester_initial_messages,
    build_tester_retest_messages,
)
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_CHAT_PROMPT_TEMPLATE,
    CODER_REPAIR_CHAT_PROMPT_TEMPLATE,
    CODER_SYSTEM_RULES,
)
from multi_agent_sdlc.models import CoderStatus, TesterStatus
from multi_agent_sdlc.state import DevState


def prepare_coder_implementation_node(
    state: DevState,
) -> dict[str, object]:
    prompt_value = CODER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_rules": CODER_SYSTEM_RULES,
            "coder_execution_input": json.dumps(
                build_coder_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "coder_status": CoderStatus.IMPLEMENTING,
        "coder_messages": prompt_value.to_messages(),
    }


def prepare_tester_node(
    state: DevState,
) -> dict[str, object]:

    coder_summary = state["current_coder_summary"]

    if coder_summary is None:
        raise ValueError("Cannot prepare the Tester without a Coder summary.")

    existing_messages = state.get("tester_messages", [])

    if existing_messages:
        messages = [
            build_tester_retest_messages(state),
        ]
    else:
        messages = build_tester_initial_messages(state)

    return {
        "tester_status": TesterStatus.TESTING,
        "tester_messages": messages,
        "current_project_verification_result": None,
    }


def prepare_coder_repair_node(
    state: DevState,
) -> dict[str, object]:
    prompt_value = CODER_REPAIR_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_repair_input": json.dumps(
                build_coder_repair_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "coder_status": CoderStatus.REPAIRING,
        "coder_messages": prompt_value.to_messages(),
        "current_coder_summary": None,
    }


def prepare_plan_review_node(
    state: DevState,
) -> dict[str, object]:
    plan = state["plan"]

    if plan is None:
        raise ValueError("Cannot prepare review for a missing plan.")

    return {
        "plan_review_status": PlanReviewStatus.AWAITING_REVIEW,
        "plan_review_decision": None,
        "plan_review_content": format_plan(plan),
    }


def prepare_planner_revision_node(
    state: DevState,
) -> dict[str, object]:
    review_decision = state["plan_review_decision"]

    if review_decision is None:
        raise ValueError("Plan review decision is missing.")

    revision_prompt = PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE.format(
        human_feedback=review_decision.feedback,
    )

    return {
        "planner_messages": [
            HumanMessage(content=revision_prompt),
        ],
    }
