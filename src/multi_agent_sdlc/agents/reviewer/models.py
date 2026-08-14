from typing import Literal

from pydantic import BaseModel, Field


class ReviewFinding(BaseModel):
    file: str | None = Field(
        default=None,
        description=(
            "Repository-relative path of the file associated with the finding, "
            "when applicable."
        ),
    )
    description: str = Field(
        description=(
            "Concise description of the concrete engineering issue identified "
            "during the review."
        ),
    )
    rationale: str = Field(
        description=(
            "Explanation of why the issue matters, including its impact on "
            "correctness, maintainability, reliability, security, architecture, "
            "or scope compliance."
        ),
    )
    required_change: str = Field(
        description=(
            "Specific outcome or correction required to resolve the finding, "
            "without providing or implementing the code change."
        ),
    )


class ReviewerSummary(BaseModel):
    overall_status: Literal["passed", "repair-required", "blocked"] = Field(
        description=(
            "Overall outcome of the code review. Use 'passed' when no material "
            "engineering issues remain, 'repair-required' when one or more "
            "material findings must be addressed, and 'blocked' when the review "
            "cannot be completed due to missing information, inaccessible "
            "evidence, or another blocking condition."
        ),
    )
    summary: str = Field(
        description=(
            "Concise overall assessment of the implementation, highlighting the "
            "main reasoning behind the review outcome."
        ),
    )
    findings: list[ReviewFinding] = Field(
        default_factory=list,
        description=(
            "Material, actionable engineering issues identified during the "
            "review. This should normally be empty when overall_status is "
            "'passed' and contain at least one finding when overall_status is "
            "'repair-required'."
        ),
    )
