from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from enum import StrEnum
from typing import Literal, TypedDict

from pydantic import BaseModel, ConfigDict, Field


class DevelopmentStatus(StrEnum):
    NOT_STARTED = "not_started"
    IMPLEMENTING = "implementing"
    REPAIRING = "repairing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class VerificationStatus(StrEnum):
    NOT_STARTED = "not_started"
    VERIFYING = "verifying"
    PASSED = "passed"
    REPAIR_REQUIRED = "repair_required"
    BLOCKED = "blocked"


class PlanReviewStatus(StrEnum):
    NOT_STARTED = "not_started"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    REJECTED = "rejected"


PlanReviewDecisionValue = Literal[
    "approved",
    "revision_required",
    "rejected",
]


class PlanReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: PlanReviewDecisionValue

    feedback: str | None = Field(
        default=None,
        description=(
            "Human feedback explaining required revisions or the reason "
            "for rejection."
        ),
    )


class PreparePlanReviewUpdate(TypedDict):
    plan_review_status: PlanReviewStatus
    plan_review_decision: PlanReviewDecision | None
    plan_review_content: str


class ReviewStatus(StrEnum):
    NOT_STARTED = "not_started"
    REVIEWING = "reviewing"
    PASSED = "passed"
    REPAIR_REQUIRED = "repair_required"
    BLOCKED = "blocked"


class ReviewCycle(BaseModel):
    cycle_number: int
    # review_status: ReviewStatus
    reviewer_summary: ReviewerSummary


class VerificationBlockDecision(StrEnum):
    RETRY = "retry"
    CODER_REPAIR = "coder-repair"
    PROCEED_WITH_OVERRIDE = "proceed-with-override"
    ABORT = "abort"


class VerificationBlockReview(BaseModel):
    decision: VerificationBlockDecision
    reason: str | None = None
