from enum import Enum
from typing import Literal

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
    acceptance_criteria: list[str] = Field(
        description="Concrete, testable conditions — this is what Tester checks against"
    )
    depends_on: list[str] = Field(
        description=(
            "Task identifiers that must complete before this task can safely "
            "begin. Use [] only when the task can safely begin immediately."
        )
    )
    target_files: list[str] = Field(
        description=(
            "File paths relative to the application's project directory. "
            "Do not include sandbox/ or the project id. "
            "Examples: src/calculator/core.py, tests/test_core.py."
        )
    )
    risk: RiskLevel = Field(description="Risk level of the task")


class DevelopmentPlan(BaseModel):
    project_id: str = Field(
        description=(
            "Unique lowercase kebab-case identifier used as the project "
            "directory under sandbox, for example terminal-calculator."
        )
    )
    goal: str = Field(description="Restated user objective")
    tasks: list[Task]
    execution_order: list[str] = Field(
        description="Task ids in dependency-resolved order"
    )
    assumptions: list[str] = Field(
        default_factory=list, description="Things the Planner assumed due to ambiguity"
    )
    out_of_scope: list[str] = Field(
        default_factory=list,
        description="Explicitly excluded to prevent unclear goals during Coder execution",
    )
