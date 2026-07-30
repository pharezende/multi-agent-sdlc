from multi_agent_sdlc.models import DevelopmentPlan


def format_plan(plan: DevelopmentPlan) -> str:
    sections = [
        "DEVELOPMENT PLAN",
        "",
        f"Goal: {plan.goal}",
        "",
        "Execution Order",
        *[f"- {item}" for item in plan.execution_order],
        "",
        "ASSUMPTIONS",
        *[f"- {item}" for item in plan.assumptions],
        "",
        "OUT OF SCOPE",
        *[f"- {item}" for item in plan.out_of_scope],
        "",
        "TASKS",
    ]

    for task in plan.tasks:
        sections.extend(
            [
                "",
                f"{task.id}. {task.title}",
                f"Description: {task.description}",
                f"Owner: {task.owner}",
                f"Risk: {task.risk}",
                f"Depends on: {', '.join(task.depends_on) or 'None'}",
                "Acceptance criteria:",
                *[f"- {criterion}" for criterion in task.acceptance_criteria],
                "Target files:",
                *[f"- {target_file}" for target_file in task.target_files],
            ]
        )

    return "\n".join(sections)
