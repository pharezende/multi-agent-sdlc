from pathlib import Path

from multi_agent_sdlc.agents.planner.models import DevelopmentPlan


def export_plan_to_markdown(
    plan: DevelopmentPlan,
    output_path: Path,
) -> None:
    markdown = format_plan_markdown(plan)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path.write_text(
        markdown,
        encoding="utf-8",
    )


def format_plan_markdown(plan: DevelopmentPlan) -> str:
    lines: list[str] = [
        "# Development Plan",
        "",
        "## Goal",
        "",
        plan.goal,
        "",
        "## Execution Order",
        "",
        *[
            f"{index}. {item}"
            for index, item in enumerate(plan.execution_order, start=1)
        ],
        "",
        "## Assumptions",
        "",
        *_format_markdown_items(plan.assumptions),
        "",
        "## Out of Scope",
        "",
        *_format_markdown_items(plan.out_of_scope),
        "",
        "## Tasks",
    ]

    for task in plan.tasks:
        lines.extend(
            [
                "",
                f"### {task.id} — {task.title}",
                "",
                f"- **Owner:** {task.owner}",
                f"- **Risk:** {task.risk}",
                (
                    "- **Depends on:** "
                    + (", ".join(task.depends_on) if task.depends_on else "None")
                ),
                "",
                "#### Description",
                "",
                task.description,
                "",
                "#### Acceptance Criteria",
                "",
                *_format_markdown_items(task.acceptance_criteria),
                "",
                "#### Target Files",
                "",
                *_format_markdown_items(task.target_files),
            ]
        )

    return "\n".join(lines)


def _format_markdown_items(items: list[str]) -> list[str]:
    if not items:
        return ["- None"]

    return [f"- {item}" for item in items]
