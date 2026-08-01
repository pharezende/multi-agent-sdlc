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
    goal: str = Field(description="Restated user objective, one or two sentences")
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
    summary: str = Field(
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


class TesterSummary(BaseModel):
    """Final structured handoff from the Tester to the Reviewer or Coder."""

    model_config = ConfigDict(extra="forbid")

    completed_task_ids: list[str] = Field(
        description=(
            "Tester-owned task identifiers completed with supporting evidence."
        )
    )

    files_created_or_modified: list[str] = Field(
        description=(
            "Project-relative Tester-owned files actually created or modified."
        )
    )

    development_dependencies_added: list[str] = Field(
        description=(
            "Development or verification dependencies actually added or changed."
        )
    )

    verification_results: list[dict[str, object]] = Field(
        description=(
            "Verification operations actually executed. Each item should include "
            "`verification_type`, `command`, `status`, `exit_code`, `summary`, "
            "and `related_task_ids`. Status must be `passed`, `failed`, "
            "`blocked`, or `not_executed`."
        )
    )

    acceptance_criteria_results: list[dict[str, object]] = Field(
        description=(
            "Results for approved acceptance criteria. Each item should include "
            "`task_id`, `criterion`, `status`, and `evidence`."
        )
    )

    tester_repairs: list[dict[str, object]] = Field(
        description=(
            "Repairs made only to Tester-owned files or verification "
            "configuration. Each item should include `description`, "
            "`files_modified`, and `verification_result`."
        )
    )

    implementation_failures: list[dict[str, object]] = Field(
        description=(
            "Observed failures attributed to Coder-owned production code or "
            "configuration. Each item should include `description`, "
            "`related_task_ids`, and `evidence`."
        )
    )

    unresolved_issues: list[dict[str, object]] = Field(
        description=(
            "Remaining failures, blockers, incomplete verification, or "
            "environment limitations. Each item should include `owner`, "
            "`description`, `related_task_ids`, and `evidence`. Owner must be "
            "`coder`, `tester`, `environment`, or `unknown`."
        )
    )

    overall_status: Literal[
        "passed",
        "failed",
        "blocked",
        "partial",
    ] = Field(description="Overall observed result of the Tester stage.")

    reviewer_notes: list[str] = Field(
        description=(
            "Concise handoff notes identifying verified behaviour, important "
            "failures, limitations, and areas requiring focused review."
        )
    )

    coder_repair_requests: list[dict[str, object]] = Field(
        description=(
            "Production defects requiring Coder repair. Each item must include "
            "`related_task_ids`, `affected_files`, `failed_criteria`, "
            "`observed_behavior`, `expected_behavior`, `evidence`, and "
            "`retest_guidance`. Leave empty when no Coder repair is required."
        )
    )
