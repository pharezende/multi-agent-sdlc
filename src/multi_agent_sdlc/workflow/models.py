from typing import TypedDict
from enum import Enum, StrEnum
from typing import Literal

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
    TESTING = "testing"
    PASSED = "passed"
    REPAIR_REQUIRED = "repair_required"
    BLOCKED = "blocked"


class PlanReviewStatus(StrEnum):
    NOT_STARTED = "not_started"
    AWAITING_REVIEW = "awaiting_review"
    APPROVED = "approved"
    REVISION_REQUIRED = "revision_required"
    REJECTED = "rejected"


class PlanReviewDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal[
        "approved",
        "revision_required",
        "rejected",
    ]

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
