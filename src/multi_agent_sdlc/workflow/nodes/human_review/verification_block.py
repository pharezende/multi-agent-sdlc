from typing import Literal

from langgraph.types import interrupt

from multi_agent_sdlc.presentation.verification_block_review import (
    format_verification_block_review,
)
from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationBlockReview,
)
from multi_agent_sdlc.workflow.state import DevState


def human_verification_block_review_node(
    state: DevState,
) -> dict[str, object]:
    tester_summary = state.get("current_tester_summary")

    if tester_summary is None:
        raise ValueError(
            "Current tester summary is required for verification block review."
        )

    response = interrupt(
        {
            "type": "verification_block_review",
            "content": format_verification_block_review(tester_summary),
        }
    )

    review = VerificationBlockReview.model_validate(response)

    return {
        "verification_block_review": review,
    }


def route_after_verification_block_review(
    state: DevState,
) -> Literal[
    "prepare_tester",
    "prepare_coder_repair",
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

    if block_review.decision == VerificationBlockDecision.PROCEED_WITH_OVERRIDE:
        return "prepare_reviewer"

    return "__end__"
