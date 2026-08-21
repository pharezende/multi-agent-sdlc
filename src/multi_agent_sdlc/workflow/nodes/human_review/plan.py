from typing import Literal

from langchain_core.runnables import RunnableConfig
from langgraph.types import interrupt

from multi_agent_sdlc.workflow.checkpointing import get_thread_id
from multi_agent_sdlc.workflow.models import PlanReviewDecision, PlanReviewStatus
from multi_agent_sdlc.workflow.run_repository import (
    WorkflowRunStatus,
    update_workflow_run_status,
)
from multi_agent_sdlc.workflow.state import DevState


def human_plan_review_node(
    state: DevState,
    config: RunnableConfig,
) -> dict[str, object]:
    configurable = config.get("configurable", {})
    predefined_decision = configurable.get("plan_review_decision")

    if predefined_decision is not None:
        response = predefined_decision
    else:
        response = interrupt(
            {
                "type": "plan_review",
                "content": state["plan_review_content"],
            }
        )

        update_workflow_run_status(
            get_thread_id(config),
            WorkflowRunStatus.RUNNING,
        )

    decision = PlanReviewDecision.model_validate(response)

    return {
        "plan_review_decision": decision,
        "plan_review_status": PlanReviewStatus(decision.decision),
    }


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
