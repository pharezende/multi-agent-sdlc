from unittest.mock import patch

import pytest

from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationBlockReview,
)
from multi_agent_sdlc.workflow.nodes.human_review.verification_block.node import (
    human_verification_block_review_node,
)
from multi_agent_sdlc.workflow.state import DevState


def test_human_verification_block_review_requires_tester_summary(
    dev_state: DevState,
) -> None:
    dev_state["current_tester_summary"] = None

    with pytest.raises(
        ValueError,
        match="Current tester summary is required for verification block review.",
    ):
        human_verification_block_review_node(dev_state)


@pytest.mark.parametrize(
    ("decision", "reason"),
    [
        (
            VerificationBlockDecision.RETRY,
            "Retry using the correct project structure.",
        ),
        (
            VerificationBlockDecision.CODER_REPAIR,
            "The implementation needs changes before verification can continue.",
        ),
        (
            VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
            "The blocker is environmental and the remaining evidence is sufficient.",
        ),
        (
            VerificationBlockDecision.ABORT,
            "Verification cannot be completed safely.",
        ),
    ],
)
def test_human_verification_block_review_stores_resume_response(
    dev_state: DevState,
    tester_summary: _TesterSummary,
    decision: VerificationBlockDecision,
    reason: str | None,
) -> None:
    dev_state["current_tester_summary"] = tester_summary

    resume_value = {
        "decision": decision.value,
        "reason": reason,
    }

    with patch(
        "multi_agent_sdlc.workflow.nodes.human_review.verification_block.node.interrupt",
        return_value=resume_value,
    ):
        result = human_verification_block_review_node(dev_state)

    review = result["verification_block_review"]

    assert isinstance(review, VerificationBlockReview)
    assert review.decision == decision
    assert review.reason == reason


def test_human_verification_block_review_passes_formatted_content_to_interrupt(
    dev_state: DevState,
    tester_summary: _TesterSummary,
) -> None:
    dev_state["current_tester_summary"] = tester_summary

    resume_value = {
        "decision": VerificationBlockDecision.RETRY.value,
        "reason": "Retry using the correct project structure",
    }

    with (
        patch(
            "multi_agent_sdlc.workflow.nodes.human_review.verification_block.node."
            "format_verification_block_review",
            return_value="FORMATTED VERIFICATION BLOCK REVIEW",
        ) as format_mock,
        patch(
            "multi_agent_sdlc.workflow.nodes.human_review.verification_block.node.interrupt",
            return_value=resume_value,
        ) as interrupt_mock,
    ):
        human_verification_block_review_node(dev_state)

    format_mock.assert_called_once_with(tester_summary)
    interrupt_mock.assert_called_once_with(
        {
            "type": "verification_block_review",
            "content": "FORMATTED VERIFICATION BLOCK REVIEW",
        }
    )
