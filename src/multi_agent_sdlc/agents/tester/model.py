from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerificationType(StrEnum):
    SYNC = "sync"
    ENTRY_POINT = "entry_point"
    PYTEST = "pytest"
    RUFF_CHECK = "ruff_check"
    RUFF_FORMAT_CHECK = "ruff_format_check"
    MYPY = "mypy"
    COMPLETE_PROJECT_VERIFICATION = "complete_project_verification"


class VerificationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verification_type: VerificationType
    command: list[str] | None = Field(
        default=None,
        description=(
            "Exact command executed for this verification result. "
            "Use None for aggregate or non-command verification results."
        ),
    )
    status: Literal[
        "passed",
        "failed",
        "blocked",
    ] = Field(
        description=(
            "Verification outcome: passed when execution succeeded, failed when "
            "verification ran and failed and blocked when it could not proceed. "
        )
    )
    exit_code: int | None = Field(
        default=None,
        description=(
            "Exit code returned by the executed command. "
            "Use None when no single command was executed."
        ),
    )
    summary: str = Field(
        min_length=1,
        description=(
            "Concise factual summary of the verification outcome. Report only "
            "observed results from executed checks or explicitly state when a "
            "verification was blocked or not executed. Do not infer that an "
            "acceptance criterion passed from indirect evidence."
        ),
    )
    verified_task_ids: list[str] = Field(
        min_length=1,
        description=(
            "Approved task identifiers for which this specific verification result "
            "provides direct verification evidence."
        ),
    )


class AcceptanceCriterionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: str = Field(min_length=1)
    criterion: str = Field(min_length=1)
    status: Literal["passed", "failed", "blocked", "not_executed"]
    evidence: str = Field(min_length=1)


class TesterRepair(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    files_modified: list[str] = Field(min_length=1)
    verification_result: str = Field(min_length=1)


class ImplementationFailure(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    related_task_ids: list[str] = Field(min_length=1)
    evidence: str = Field(min_length=1)


class UnresolvedIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner: Literal["coder", "tester", "environment", "tooling", "unknown"]
    description: str = Field(min_length=1)
    related_task_ids: list[str]
    evidence: str = Field(min_length=1)


class CoderRepairRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    related_task_ids: list[str] = Field(min_length=1)
    affected_files: list[str] = Field(min_length=1)
    failed_criteria: list[str] = Field(min_length=1)
    observed_behavior: str = Field(min_length=1)
    expected_behavior: str = Field(min_length=1)
    evidence: str = Field(min_length=1)


class TesterSummary(BaseModel):
    """Final structured handoff from the Tester to the Reviewer or Coder."""

    model_config = ConfigDict(extra="forbid")

    addressed_task_ids: list[str] = Field(
        description=(
            "Tester-owned task identifiers actively worked on during this cycle, "
            "including test implementation, Tester-owned repairs, verification, "
            "or investigation. Include blocked Tester-owned tasks that were "
            "attempted. Do not include Coder-owned tasks merely because their "
            "implementation was verified."
        )
    )

    passed_task_ids: list[str] = Field(
        description=(
            "Tester-owned task identifiers whose applicable acceptance criteria "
            "all passed with supporting evidence. Do not include Coder-owned tasks "
            "or Tester-owned tasks that are failed, blocked, incomplete, or "
            "unresolved."
        )
    )

    related_task_ids: list[str] = Field(
        description=(
            "Approved task identifiers owned by other agents whose outputs were "
            "evaluated, exercised, or affected during this Tester cycle. Do not "
            "include Tester-owned tasks listed in addressed_task_ids."
        )
    )

    files_created_or_modified: list[str] = Field(
        description=(
            "Project-relative Tester-owned files actually created or modified."
        )
    )

    development_dependencies_added: list[str] = Field(
        description=(
            "Development dependencies newly added by the Tester during this cycle. "
            "Do not include dependencies that were already present or merely used. "
            "Include version constraints exactly as written in project configuration."
        )
    )
    verification_results: list[VerificationResult] = Field(
        description=(
            "Verification operations actually executed. This field must contain "
            "sufficient successful evidence when overall_status is passed."
        )
    )

    acceptance_criteria_results: list[AcceptanceCriterionResult] = Field(
        description=(
            "Results for all applicable approved acceptance criteria when "
            "overall_status is passed."
        )
    )

    tester_repairs: list[TesterRepair] = Field(
        description=(
            "Repairs made only to Tester-owned files or verification configuration."
        )
    )

    implementation_failures: list[ImplementationFailure] = Field(
        description=(
            "Failures attributed to Coder-owned production code or configuration."
        )
    )

    unresolved_issues: list[UnresolvedIssue] = Field(
        description=(
            "Issues that remain unresolved, could not be safely classified, or "
            "prevented required verification from completing. Do not duplicate "
            "confirmed Coder-owned defects already recorded in "
            "implementation_failures and coder_repair_requests. This field "
            "should normally be non-empty only when overall_status is blocked."
        )
    )

    overall_status: Literal["passed", "repair-required", "blocked"] = Field(
        description=(
            "Final Tester outcome. Use passed only when the latest complete "
            "project verification passed and every applicable acceptance criterion "
            "passed. Use failed when verification produced evidence of at least "
            "one Coder-owned production defect requiring repair. Use blocked only "
            "when required verification could not be completed or a failure could "
            "not be safely classified because of an external, environmental, tool, "
            "dependency, or access limitation."
        )
    )

    coder_repair_requests: list[CoderRepairRequest] = Field(
        description=("Focused production defects requiring repair by the Coder.")
    )


class TesterCycle(BaseModel):
    cycle_number: int
    tester_summary: TesterSummary
