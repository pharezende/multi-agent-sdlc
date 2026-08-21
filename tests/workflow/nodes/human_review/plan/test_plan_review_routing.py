from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.nodes.human_review import route_after_plan_review
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_plan_review_approved_to_prepare_coder_implementation(
    dev_state: DevState,
) -> None:
    dev_state["plan_review_status"] = PlanReviewStatus.APPROVED

    assert route_after_plan_review(dev_state) == "prepare_coder_implementation"


def test_route_after_plan_review_revision_required_to_prepare_planner_revision(
    dev_state: DevState,
) -> None:
    dev_state["plan_review_status"] = PlanReviewStatus.REVISION_REQUIRED

    assert route_after_plan_review(dev_state) == "prepare_planner_revision"


def test_route_after_plan_review_failed_to_end(dev_state: DevState) -> None:
    dev_state["plan_review_status"] = PlanReviewStatus.REJECTED

    assert route_after_plan_review(dev_state) == "__end__"
