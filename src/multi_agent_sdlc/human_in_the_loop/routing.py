from multi_agent_sdlc.workflow.state import DevState
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from typing import Literal


def route_after_plan_review(
    state: DevState,
) -> Literal[
    "prepare_coder_implementation",
    "prepare_planner_revision",
    "__end__",
]:
    status = state["plan_review_status"]

    if status == PlanReviewStatus.APPROVED:
        return "prepare_coder_implementation"

    if status == PlanReviewStatus.REVISION_REQUIRED:
        return "prepare_planner_revision"

    return "__end__"
