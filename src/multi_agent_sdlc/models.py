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
    title: str = Field(
        description="Short title of the project, only three words at most"
    )
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
        description="Explicitly excluded to prevent scope creep during Coder execution",
    )
