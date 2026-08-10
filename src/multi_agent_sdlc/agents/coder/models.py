from typing import TypedDict
from enum import Enum, StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
            "Command-line entry-point names configured under " "[project.scripts]."
        ),
    )

    executed_operations: list[str] = Field(
        default_factory=list,
        description=(
            "Operations actually executed by Coder tools and their observed "
            "outcomes, such as successful uv sync or application launch."
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


class CoderCycle(BaseModel):
    cycle_number: int
    coder_summary: CoderSummary
