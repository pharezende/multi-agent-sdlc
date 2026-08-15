from multi_agent_sdlc.workflow.models import VerificationBlockDecision
from multi_agent_sdlc.workflow.models import VerificationBlockReview
from multi_agent_sdlc.human_in_the_loop.verification_block_review.routing import (
    route_after_verification_block_review,
)
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


def test_route_after_verification_block_review_retries_tester() -> None:
    state: DevState = build_initial_state("test request")
    state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.RETRY,
        reason="Retry verification with the corrected verification context.",
    )

    result = route_after_verification_block_review(state)

    assert result == "prepare_tester"


def test_route_after_verification_block_review_routes_to_coder_repair() -> None:
    state: DevState = build_initial_state("test request")
    state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.CODER_REPAIR,
        reason="The implementation requires changes.",
    )

    result = route_after_verification_block_review(state)

    assert result == "prepare_coder_repair"


def test_route_after_verification_block_review_proceeds_with_override() -> None:
    state: DevState = build_initial_state("test request")
    state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
        reason="The verification blocker is accepted by the human reviewer.",
    )

    result = route_after_verification_block_review(state)

    assert result == "prepare_reviewer"


def test_route_after_verification_block_review_aborts_workflow() -> None:
    state: DevState = build_initial_state("test request")
    state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.ABORT,
        reason="The workflow cannot safely continue.",
    )

    result = route_after_verification_block_review(state)

    assert result == "__end__"
