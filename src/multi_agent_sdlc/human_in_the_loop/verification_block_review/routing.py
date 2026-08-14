from typing import Literal
from multi_agent_sdlc.workflow.state import DevState
from multi_agent_sdlc.workflow.models import VerificationBlockDecision


def route_after_verification_block_review(
    state: DevState,
) -> Literal[
    "prepare_tester",
    "prepare_coder_repair",
    "prepare_planner_revision",
    "prepare_reviewer",
    "__end__",
]:
    block_review = state.get("verification_block_review")

    if block_review is None:
        raise ValueError("Verification block review is required.")

    if block_review.decision == VerificationBlockDecision.RETRY:
        return "prepare_tester"

    if block_review.decision == VerificationBlockDecision.CODER_REPAIR:
        return "prepare_coder_repair"

    if block_review.decision == VerificationBlockDecision.PLAN_REVISION:
        return "prepare_planner_revision"

    if block_review.decision == VerificationBlockDecision.PROCEED_WITH_OVERRIDE:
        return "prepare_reviewer"

    return "__end__"
