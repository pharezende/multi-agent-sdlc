from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationBlockReview,
)
from multi_agent_sdlc.workflow.nodes.human_review import (
    route_after_verification_block_review,
)
from multi_agent_sdlc.workflow.state import DevState


def test_route_after_verification_block_review_retries_tester(
    dev_state: DevState,
) -> None:
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.RETRY,
        reason="Retry verification with the corrected verification context.",
    )

    assert route_after_verification_block_review(dev_state) == "prepare_tester"


def test_route_after_verification_block_review_routes_to_coder_repair(
    dev_state: DevState,
) -> None:
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.CODER_REPAIR,
        reason="The implementation requires changes.",
    )

    assert (
        route_after_verification_block_review(dev_state) == "prepare_coder_repair"
    )


def test_route_after_verification_block_review_proceeds_with_override(
    dev_state: DevState,
) -> None:
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
        reason="The verification blocker is accepted by the human reviewer.",
    )

    assert route_after_verification_block_review(dev_state) == "prepare_reviewer"


def test_route_after_verification_block_review_aborts_workflow(
    dev_state: DevState,
) -> None:
    dev_state["verification_block_review"] = VerificationBlockReview(
        decision=VerificationBlockDecision.ABORT,
        reason="The workflow cannot safely continue.",
    )

    assert route_after_verification_block_review(dev_state) == "__end__"
