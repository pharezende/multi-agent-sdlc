from multi_agent_sdlc.presentation.format import format_verification_block_review
from multi_agent_sdlc.workflow.models import VerificationBlockReview
from multi_agent_sdlc.workflow.models import VerificationBlockDecision
from langgraph.types import interrupt
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
        "verification_block_decision": review.decision,
    }
