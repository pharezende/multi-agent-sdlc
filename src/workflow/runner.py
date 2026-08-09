from multi_agent_sdlc.presentation.terminal_plan_review import (
    collect_plan_review_decision,
)
from workflow.graph import build_graph
from typing import Any
from workflow.checkpointing import build_workflow_config
from workflow.state import build_initial_state
from workflow.run_repository import WorkflowRun
from workflow.run_repository import get_workflow_run
from workflow.checkpointing import create_checkpointer
from workflow.run_repository import WorkflowRunStatus
from workflow.run_repository import update_workflow_run_status
from workflow.run_repository import create_workflow_run
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command


def run_new_workflow(request: str, plan_review_decision: dict[str, Any]) -> None:
    workflow_run = create_workflow_run(request)

    config = build_workflow_config(workflow_run.thread_id, plan_review_decision)

    initial_state = build_initial_state(request)

    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        result = graph.invoke(
            initial_state,
            config=config,
        )

        _process_workflow_result(
            graph,
            result,
            workflow_run,
            config,
        )


def resume_workflow(thread_id: str, plan_review_decision: dict[str, Any]) -> None:
    workflow_run = get_workflow_run(thread_id)

    if workflow_run is None:
        raise ValueError(f"Workflow with thread id {thread_id!r} was not found.")

    if workflow_run.status in {
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.FAILED,
    }:
        raise ValueError(
            f"Workflow run {thread_id} cannot be resumed because "
            f"its status is {workflow_run.status!r}."
        )

    config = build_workflow_config(workflow_run.thread_id, plan_review_decision)

    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        snapshot = graph.get_state(config)

        if snapshot.interrupts:
            interrupt_value = snapshot.interrupts[0].value

            if interrupt_value["type"] != "plan_review":
                raise ValueError(
                    f"Unsupported interrupt type: " f"{interrupt_value['type']!r}"
                )

            print()
            print(interrupt_value["content"])
            print("\nGraph paused for plan review.")

            review_response = collect_plan_review_decision()

            update_workflow_run_status(
                workflow_run.thread_id,
                WorkflowRunStatus.RUNNING,
            )

            result = graph.invoke(
                Command(resume=review_response),
                config=config,
            )

        elif snapshot.next:
            update_workflow_run_status(
                workflow_run.thread_id,
                WorkflowRunStatus.RUNNING,
            )

            result = graph.invoke(
                None,
                config=config,
            )

        else:
            raise ValueError(
                f"Workflow run {workflow_run.thread_id} " "has no pending work."
            )

        _process_workflow_result(
            graph,
            result,
            workflow_run,
            config,
        )


def _process_workflow_result(
    graph,
    result: dict[str, Any],
    workflow_run: WorkflowRun,
    config: RunnableConfig,
) -> None:
    interrupts = result.get("__interrupt__", ())

    while interrupts:
        interrupt_value = interrupts[0].value

        update_workflow_run_status(
            workflow_run.thread_id,
            WorkflowRunStatus.INTERRUPTED,
        )

        if interrupt_value["type"] != "plan_review":
            raise ValueError(
                f"Unsupported interrupt type: " f"{interrupt_value['type']!r}"
            )

        print()
        print(interrupt_value["content"])
        print("\nGraph paused for plan review.")

        review_response = collect_plan_review_decision()

        update_workflow_run_status(
            workflow_run.thread_id,
            WorkflowRunStatus.RUNNING,
        )

        result = graph.invoke(
            Command(resume=review_response),
            config=config,
        )

        interrupts = result.get("__interrupt__", ())

    update_workflow_run_status(
        workflow_run.thread_id,
        WorkflowRunStatus.COMPLETED,
    )

    print("\nWorkflow execution completed.")
