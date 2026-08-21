import pytest

from multi_agent_sdlc.presentation.terminal_verification_block_review import (
    collect_verification_block_review,
)
from multi_agent_sdlc.workflow.models import (
    VerificationBlockDecision,
    VerificationBlockReview,
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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

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
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    review = collect_verification_block_review()
    captured = capsys.readouterr()

    assert review.decision == decision
    assert review.reason == "Valid reason"
    assert "Reason is required." in captured.out
