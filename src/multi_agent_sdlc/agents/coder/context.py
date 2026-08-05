from multi_agent_sdlc.state import DevState
from typing import Any


def build_coder_context(state: DevState) -> dict[str, Any]:

    plan = state["plan"]
    coder_tasks = [
        task.model_dump(mode="json") for task in plan.tasks if task.owner == "coder"
    ]

    if not coder_tasks:
        raise ValueError("The approved plan contains no Coder-owned tasks.")

    return {
        "project_directory": str(state["project_directory"]),
        "project_id": plan.project_id,
        "goal": plan.goal,
        "assumptions": plan.assumptions,
        "out_of_scope": plan.out_of_scope,
        "tasks": coder_tasks,
    }
