from typing import Literal
from turtle import title
from enum import Enum
from typing import List
from pydantic import BaseModel, Field


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
