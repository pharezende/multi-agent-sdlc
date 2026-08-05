from multi_agent_sdlc.tools.tester.validation import NonBlankStr
from enum import StrEnum
from typing import Literal
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    id: str = Field(description="Short unique id, e.g. 'T1', 'T2'")
    title: str = Field(description="Title of the task")
    owner: Literal["coder", "tester"] = Field(
        description=(
            "Owner of the task. "
            "Use 'coder' for production code, application configuration, "
            "runtime behaviour, and implementation documentation. "
            "Use 'tester' for unit tests, integration tests, fixtures, mocks, "
            "test data, coverage configuration, and test documentation. "
            "A task must have exactly one owner. Do not assign test creation "
            "or test-file changes to the coder."
        )
    )
    description: str = Field(
        description="What needs to be built/changed, specific enough for Coder to act without re-asking"
    )
    acceptance_criteria: List[str] = Field(
        description="Concrete, testable conditions — this is what Tester checks against"
    )
    depends_on: List[str] = Field(
        default_factory=list, description="Task ids that must complete first"
    )
    target_files: list[str] = Field(
        description=(
            "File paths relative to the application's project directory. "
            "Do not include `sandbox/` or the project id. "
            "Examples: `src/calculator/core.py`, `tests/test_core.py`."
        )
    )
    risk: RiskLevel = Field(description="Risk level of the task")


class DevelopmentPlan(BaseModel):
    project_id: str = Field(
        description=(
            "Unique lowercase kebab-case identifier used as the project "
            "directory under `sandbox`, for example `terminal-calculator`."
        )
    )
    goal: str = Field(description="Restated user objective")
    tasks: List[Task]
    execution_order: List[str] = Field(
        description="Task ids in dependency-resolved order — Planner computes this so downstream nodes don't need a topo-sort"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Things the Planner assumed due to ambiguity"
    )
    out_of_scope: List[str] = Field(
        default_factory=list,
        description="Explicitly excluded to prevent unclear goals during Coder execution",
    )


class CoderSummary(BaseModel):
    implementation_summary: str = Field(
        description=(
            "Brief factual summary of the production implementation completed "
            "by the Coder. Do not include unverified test or quality claims."
        )
    )

    completed_task_ids: list[str] = Field(
        default_factory=list,
        description=(
            "Identifiers of Coder-owned plan tasks that were implemented. "
            "Include only tasks supported by completed file operations."
        ),
    )

    modified_files: list[str] = Field(
        default_factory=list,
        description=(
            "Project-relative paths of production files created or modified "
            "by the Coder. Do not include test files."
        ),
    )

    runtime_dependencies: list[str] = Field(
        default_factory=list,
        description=(
            "Production runtime dependencies added to the project. "
            "Do not include testing, linting, coverage, or type-checking tools."
        ),
    )

    entry_points: list[str] = Field(
        default_factory=list,
        description=(
            "Command-line entry-point names configured under " "`[project.scripts]`."
        ),
    )

    executed_operations: list[str] = Field(
        default_factory=list,
        description=(
            "Operations actually executed by Coder tools and their observed "
            "outcomes, such as successful `uv sync` or application launch."
        ),
    )

    unresolved_issues: list[str] = Field(
        default_factory=list,
        description=(
            "Known implementation problems, blockers, uncertainties, or "
            "failed operations that remain unresolved."
        ),
    )

    tester_notes: list[str] = Field(
        default_factory=list,
        description=(
            "Concise handoff notes identifying behaviour or acceptance "
            "criteria the Tester should verify. Do not claim they already pass."
        ),
    )


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
    command: list[str] = Field(min_length=1)
    status: Literal["passed", "failed", "blocked", "not_executed"]
    exit_code: int | None
    summary: str = Field(min_length=1)
    related_task_ids: list[str]


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

    owner: Literal["coder", "tester", "environment", "unknown"]
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

    addressed_task_ids: list[NonBlankStr] = Field(
        description=(
            "Tester-owned task identifiers actively worked on during this cycle, "
            "including test implementation, Tester-owned repairs, verification, "
            "or investigation. Include blocked Tester-owned tasks that were "
            "attempted. Do not include Coder-owned tasks merely because their "
            "implementation was verified."
        )
    )

    passed_task_ids: list[NonBlankStr] = Field(
        description=(
            "Tester-owned task identifiers whose applicable acceptance criteria "
            "all passed with supporting evidence. Do not include Coder-owned tasks "
            "or Tester-owned tasks that are failed, blocked, incomplete, or "
            "unresolved."
        )
    )

    related_task_ids: list[NonBlankStr] = Field(
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
            "sufficient successful evidence when `overall_status` is `passed`."
        )
    )

    acceptance_criteria_results: list[AcceptanceCriterionResult] = Field(
        description=(
            "Results for all applicable approved acceptance criteria when "
            "`overall_status` is `passed`."
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
            "`implementation_failures` and `coder_repair_requests`. This field "
            "should normally be non-empty only when `overall_status` is `blocked`."
        )
    )

    overall_status: Literal["passed", "failed", "blocked"] = Field(
        description=(
            "Final Tester outcome. Use `passed` only when the latest complete "
            "project verification passed and every applicable acceptance criterion "
            "passed. Use `failed` when verification produced evidence of at least "
            "one Coder-owned production defect requiring repair. Use `blocked` only "
            "when required verification could not be completed or a failure could "
            "not be safely classified because of an external, environmental, tool, "
            "dependency, or access limitation."
        )
    )

    coder_repair_requests: list[CoderRepairRequest] = Field(
        description=("Focused production defects requiring repair by the Coder.")
    )


class VerificationCycle(BaseModel):
    cycle_number: int
    tester_summary: TesterSummary


class CoderMode(StrEnum):
    IMPLEMENTATION = "implementation"
    REPAIR = "repair"


class ImplementationCycle(BaseModel):
    cycle_number: int
    # mode: CoderMode
    coder_summary: CoderSummary


class CoderStatus(StrEnum):
    IMPLEMENTING = "implementing"
    REPAIRING = "repairing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"


class TesterStatus(StrEnum):
    TESTING = "testing"
    PASSED = "passed"
    REPAIR_REQUIRED = "repair_required"
    BLOCKED = "blocked"
