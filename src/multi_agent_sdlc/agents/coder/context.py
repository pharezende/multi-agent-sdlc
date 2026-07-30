from multi_agent_sdlc.state import DevState
from typing import Any


def build_coder_context(state: DevState) -> dict[str, Any]:

    plan = state.get("plan")
    coder_tasks = [
        task.model_dump(mode="json") for task in plan.tasks if task.owner == "coder"
    ]

    return {
        "request": state.get("request"),
        "project_directory": state.get("project_directory"),
        "assumptions": plan.assumptions,
        "out_of_scope": plan.out_of_scope,
        "tasks": coder_tasks,
    }
