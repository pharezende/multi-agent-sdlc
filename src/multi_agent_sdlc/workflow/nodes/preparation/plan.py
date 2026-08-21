from langchain_core.messages import HumanMessage

from multi_agent_sdlc.agents.planner.prompt import (
    PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE,
)
from multi_agent_sdlc.presentation.plan_text import format_plan
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.state import DevState


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
) -> dict[str, list[HumanMessage]]:
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
