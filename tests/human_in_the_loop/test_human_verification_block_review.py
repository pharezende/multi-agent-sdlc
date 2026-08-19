from multi_agent_sdlc.workflow.state import build_initial_state
from multi_agent_sdlc.agents.tester.model import TesterSummary as _TesterSummary
from multi_agent_sdlc.workflow.models import VerificationBlockReview
from multi_agent_sdlc.presentation.terminal_verification_block_review import (
    collect_verification_block_review,
)
from multi_agent_sdlc.workflow.models import VerificationBlockDecision
from unittest.mock import patch

import pytest


from multi_agent_sdlc.human_in_the_loop.verification_block_review.verification_block_review import (
    human_verification_block_review_node,
)
from multi_agent_sdlc.workflow.state import DevState


@pytest.fixture
def dev_state() -> DevState:
    return build_initial_state("test request")


@pytest.fixture
def tester_summary() -> _TesterSummary:
    return _TesterSummary(
        addressed_task_ids=["T2"],
        passed_task_ids=[],
        related_task_ids=["T1"],
        files_created_or_modified=[],
        development_dependencies_added=[],
        verification_results=[],
        acceptance_criteria_results=[],
        tester_repairs=[],
        implementation_failures=[],
        unresolved_issues=[
            # ...
        ],
        overall_status="blocked",
        coder_repair_requests=[],
    )


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
        "multi_agent_sdlc.human_in_the_loop.verification_block_review."
        "verification_block_review.interrupt",
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
            "multi_agent_sdlc.human_in_the_loop.verification_block_review."
            "verification_block_review.format_verification_block_review",
            return_value="FORMATTED VERIFICATION BLOCK REVIEW",
        ) as format_mock,
        patch(
            "multi_agent_sdlc.human_in_the_loop.verification_block_review."
            "verification_block_review.interrupt",
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


def test_collect_verification_block_review_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            "1",
            "Retry using the correct project structure",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    assert review == VerificationBlockReview(
        decision=VerificationBlockDecision.RETRY,
        reason="Retry using the correct project structure",
    )


def test_collect_verification_block_review_coder_repair(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            "2",
            "The implementation needs repair.",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    assert review == VerificationBlockReview(
        decision=VerificationBlockDecision.CODER_REPAIR,
        reason="The implementation needs repair.",
    )


def test_collect_verification_block_review_proceed_with_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            "3",
            "The blocker is environmental and can be safely overridden.",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    assert review == VerificationBlockReview(
        decision=VerificationBlockDecision.PROCEED_WITH_OVERRIDE,
        reason="The blocker is environmental and can be safely overridden.",
    )


def test_collect_verification_block_review_abort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    responses = iter(
        [
            "4",
            "Verification cannot proceed safely.",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    assert review == VerificationBlockReview(
        decision=VerificationBlockDecision.ABORT,
        reason="Verification cannot proceed safely.",
    )


def test_collect_verification_block_review_reprompts_invalid_option(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    responses = iter(
        [
            "9",
            "1",
            "Retry using the correct project structure",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    captured = capsys.readouterr()

    assert review.decision == VerificationBlockDecision.RETRY
    assert "Invalid option" in captured.out


@pytest.mark.parametrize(
    ("option", "decision"),
    [
        ("1", VerificationBlockDecision.RETRY),
        ("2", VerificationBlockDecision.CODER_REPAIR),
        ("3", VerificationBlockDecision.PROCEED_WITH_OVERRIDE),
        ("4", VerificationBlockDecision.ABORT),
    ],
)
def test_collect_verification_block_review_requires_reason(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    option: str,
    decision: VerificationBlockDecision,
) -> None:
    responses = iter(
        [
            option,
            "",
            "Valid reason",
        ]
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(responses),
    )

    review = collect_verification_block_review()

    captured = capsys.readouterr()

    assert review.decision == decision
    assert review.reason == "Valid reason"
    assert "Reason is required." in captured.out
