from langchain_core.messages import HumanMessage

from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.workflow.models import (
    PlanReviewDecision,
    PlanReviewDecisionValue,
    PlanReviewStatus,
)
from multi_agent_sdlc.workflow.nodes.preparation.plan import (
    prepare_plan_review_node,
    prepare_planner_revision_node,
)
from multi_agent_sdlc.workflow.state import DevState


def build_plan_review_decision(
    decision: PlanReviewDecisionValue = "approved",
    feedback: str | None = None,
) -> PlanReviewDecision:
    return PlanReviewDecision(
        decision=decision,
        feedback=feedback,
    )


def test_prepare_plan_review_node_sets_state(
    dev_state: DevState,
    development_plan: DevelopmentPlan,
) -> None:
    dev_state["plan"] = development_plan

    result = prepare_plan_review_node(dev_state)

    assert result["plan_review_status"] == PlanReviewStatus.AWAITING_REVIEW
    assert result["plan_review_decision"] is None


def test_prepare_planner_revision_sets_planner_messages(
    dev_state: DevState,
) -> None:
    dev_state["plan_review_decision"] = build_plan_review_decision(
        decision="revision_required",
        feedback="Add more verification tasks.",
    )
    result = prepare_planner_revision_node(dev_state)

    messages = result["planner_messages"]

    assert isinstance(messages, list)
    assert len(messages) == 1
    assert isinstance(messages[0], HumanMessage)
    assert "Add more verification tasks." in messages[0].content
