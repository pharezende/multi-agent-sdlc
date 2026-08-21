from multi_agent_sdlc.agents.reviewer.messages import (
    build_reviewer_initial_messages,
    build_reviewer_initial_override_messages,
    build_reviewer_rereview_messages,
    build_reviewer_rereview_override_messages,
)
from multi_agent_sdlc.workflow.models import ReviewStatus, VerificationBlockDecision
from multi_agent_sdlc.workflow.state import DevState


def prepare_reviewer_node(
    state: DevState,
) -> dict[str, object]:
    reviewer_history = state.get("reviewer_summary_history", [])
    verification_block_review = state.get("verification_block_review")

    if (
        verification_block_review is not None
        and verification_block_review.decision
        == VerificationBlockDecision.PROCEED_WITH_OVERRIDE
    ):
        if not reviewer_history:
            reviewer_messages = build_reviewer_initial_override_messages(state)
        else:
            reviewer_messages = [
                *state["reviewer_messages"],
                *build_reviewer_rereview_override_messages(state),
            ]
    elif not reviewer_history:
        reviewer_messages = build_reviewer_initial_messages(state)
    else:
        reviewer_messages = [
            *state["reviewer_messages"],
            *build_reviewer_rereview_messages(state),
        ]

    return {
        "reviewer_messages": reviewer_messages,
        "review_status": ReviewStatus.REVIEWING,
        "current_reviewer_summary": None,
    }
