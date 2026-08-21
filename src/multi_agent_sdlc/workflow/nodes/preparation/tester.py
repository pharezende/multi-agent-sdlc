from multi_agent_sdlc.agents.tester.messages import (
    build_tester_initial_messages,
    build_tester_retest_messages,
    build_tester_verification_retry_message,
)
from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationStatus,
)
from multi_agent_sdlc.workflow.state import DevState


def prepare_tester_node(
    state: DevState,
) -> dict[str, object]:
    verification_block_review = state["verification_block_review"]

    if (
        verification_block_review is not None
        and verification_block_review.decision == VerificationBlockDecision.RETRY
    ):
        messages = build_tester_verification_retry_message(state)
    else:
        coder_summary = state["current_coder_summary"]

        if coder_summary is None:
            raise ValueError("Cannot prepare the Tester without a Coder summary.")

        existing_messages = state.get("tester_messages", [])

        if existing_messages:
            messages = [
                build_tester_retest_messages(state),
            ]
        else:
            messages = build_tester_initial_messages(state)

    return {
        "verification_status": VerificationStatus.VERIFYING,
        "tester_messages": messages,
        "current_project_verification_result": None,
    }
