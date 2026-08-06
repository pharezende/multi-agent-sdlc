from multi_agent_sdlc.models import DevelopmentPlan


def format_plan(plan: DevelopmentPlan) -> str:
    lines: list[str] = [
        "DEVELOPMENT PLAN",
        "=" * 72,
        "",
        "GOAL",
        plan.goal,
        "",
        "EXECUTION ORDER",
        *[
            f"{index}. {item}"
            for index, item in enumerate(plan.execution_order, start=1)
        ],
        "",
        "ASSUMPTIONS",
        *format_items(plan.assumptions),
        "",
        "OUT OF SCOPE",
        *format_items(plan.out_of_scope),
        "",
        "TASKS",
        "=" * 72,
    ]

    for task in plan.tasks:
        lines.extend(
            [
                "",
                f"{task.id} — {task.title}",
                "-" * 72,
                f"Owner: {task.owner}",
                f"Risk: {task.risk}",
                (
                    "Depends on: "
                    + (", ".join(task.depends_on) if task.depends_on else "None")
                ),
                "",
                "Description",
                task.description,
                "",
                "Acceptance criteria",
                *format_items(
                    task.acceptance_criteria,
                    indentation="  ",
                ),
                "",
                "Target files",
                *format_items(
                    task.target_files,
                    indentation="  ",
                ),
            ]
        )

    return "\n".join(lines)


def format_items(
    items: list[str],
    *,
    indentation: str = "",
) -> list[str]:
    if not items:
        return [f"{indentation}- None"]

    return [f"{indentation}- {item}" for item in items]
