from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

NonBlankStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class CoderSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    implementation_summary: NonBlankStr = Field(
        description=(
            "Brief factual summary of the production implementation completed "
            "by the Coder. Do not include unverified test or quality claims."
        )
    )

    completed_task_ids: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Identifiers of Coder-owned plan tasks that were implemented. "
            "Include only tasks supported by completed file operations."
        ),
    )

    modified_files: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Project-relative paths of production files created or modified "
            "by the Coder. Do not include test files."
        ),
    )

    runtime_dependencies: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Production runtime dependencies added to the project. "
            "Do not include testing, linting, coverage, or type-checking tools."
        ),
    )

    entry_points: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Command-line entry-point names configured under [project.scripts]."
        ),
    )

    executed_operations: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Operations actually executed by Coder tools and their observed "
            "outcomes, such as successful uv sync or application launch."
        ),
    )

    unresolved_issues: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Known implementation problems, blockers, uncertainties, or "
            "failed operations that remain unresolved."
        ),
    )

    tester_notes: list[NonBlankStr] = Field(
        default_factory=list,
        description=(
            "Concise handoff notes identifying behaviour or acceptance "
            "criteria the Tester should verify. Do not claim they already pass."
        ),
    )

    @model_validator(mode="after")  # TODO: Send error to the LLM later.
    def validate_completion_evidence(self) -> "CoderSummary":
        if not self.completed_task_ids and not self.unresolved_issues:
            raise ValueError(
                "The Coder summary must report at least one completed task "
                "or at least one unresolved issue."
            )

        return self


class CoderCycle(BaseModel):
    cycle_number: int
    coder_summary: CoderSummary
