from typing import Any

from multi_agent_sdlc.workflow.state import DevState


def build_coder_implementation_context(state: DevState) -> dict[str, Any]:

    plan = state.get("plan")
    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")
    coder_tasks = [
        task.model_dump(mode="json") for task in plan.tasks if task.owner == "coder"
    ]

    if not coder_tasks:
        raise ValueError("The approved plan contains no Coder-owned tasks.")

    return {
        "request": state["request"],
        "project_id": plan.project_id,
        "goal": plan.goal,
        "assumptions": plan.assumptions,
        "out_of_scope": plan.out_of_scope,
        "tasks": coder_tasks,
    }


def build_coder_repair_context(
    state: DevState,
) -> dict[str, object]:
    plan = state["plan"]
    if plan is None:
        raise ValueError("This workflow stage requires an approved plan.")
    tester_summary = state["current_tester_summary"]
    if tester_summary is None:
        raise ValueError("This workflow stage requires a tester summary.")

    related_task_ids = {
        task_id
        for repair_request in tester_summary.coder_repair_requests
        for task_id in repair_request.related_task_ids
    }

    related_task_ids.update(
        task_id
        for failure in tester_summary.implementation_failures
        for task_id in failure.related_task_ids
    )

    related_coder_tasks = [
        task.model_dump(mode="json")
        for task in plan.tasks
        if task.owner == "coder" and task.id in related_task_ids
    ]

    return {
        "related_coder_tasks": related_coder_tasks,
        "coder_repair_requests": [
            request.model_dump(mode="json")
            for request in tester_summary.coder_repair_requests
        ],
        "implementation_failures": [
            failure.model_dump(mode="json")
            for failure in tester_summary.implementation_failures
        ],
        "failed_acceptance_criteria": [
            result.model_dump(mode="json")
            for result in tester_summary.acceptance_criteria_results
            if result.status == "failed" and result.task_id in related_task_ids
        ],
        "failed_verification_results": [
            result.model_dump(mode="json")
            for result in tester_summary.verification_results
            if result.status == "failed"
        ],
    }
