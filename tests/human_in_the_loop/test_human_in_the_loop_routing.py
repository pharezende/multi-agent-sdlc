from multi_agent_sdlc.human_in_the_loop.routing import route_after_plan_review
from multi_agent_sdlc.workflow.models import PlanReviewStatus
from multi_agent_sdlc.workflow.state import build_initial_state
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_plan_review_approved_to_prepare_coder_implementation():
    state: DevState = build_initial_state("test request")
    state["plan_review_status"] = PlanReviewStatus.APPROVED

    assert route_after_plan_review(state) == "prepare_coder_implementation"


def test_route_after_plan_review_revision_required_to_prepare_planner_revision():
    state: DevState = build_initial_state("test request")
    state["plan_review_status"] = PlanReviewStatus.REVISION_REQUIRED

    assert route_after_plan_review(state) == "prepare_planner_revision"


def test_route_after_plan_review_failed_to_end():
    state: DevState = build_initial_state("test request")
    state["plan_review_status"] = PlanReviewStatus.REJECTED

    assert route_after_plan_review(state) == "__end__"
