from typing import Any
from workflow.checkpointing import build_workflow_config
from multi_agent_sdlc.state import build_initial_state
from workflow.runs import WorkflowRun
from workflow.runs import get_workflow_run
from workflow.checkpointing import create_checkpointer
from workflow.runs import WorkflowRunStatus
from workflow.runs import update_workflow_run_status
from workflow.runs import create_workflow_run
from workflow.runs import initialize_workflow_runs_database
from multi_agent_sdlc.agents.presentation.terminal_plan_review import (
    collect_plan_review_decision,
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph

import argparse
from langgraph.types import Command

from .graph import build_graph


def generate_diagram(graph: CompiledStateGraph) -> None:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("multi_agent_sdlc_workflow.png", "wb") as file:
        file.write(png_data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-agent SDLC workflow.")

    parser.add_argument(
        "--resume",
        metavar="THREAD_ID",
        help="Resume the workflow identified by THREAD_ID.",
    )

    return parser.parse_args()


def run() -> None:
    args = parse_args()

    initialize_workflow_runs_database()

    if args.resume:
        resume_workflow(
            thread_id=args.resume,
        )
    else:
        request = """
        Build a local task-management REST API that lets users create, retrieve,
        update, delete, and list tasks. Each task must include an ID, title,
        optional description, priority, status, creation timestamp, optional due
        date, and tags. Support filtering by status, priority, tag, and due-date
        range, as well as sorting and pagination.

        Store data locally in SQLite and ensure database initialization happens
        automatically. Enforce valid task-state transitions, such as preventing
        a completed task from being moved directly back to in_progress without
        first reopening it. Validate all inputs and return appropriate HTTP
        status codes and structured error responses.

        Add an endpoint that returns task statistics, including total tasks,
        counts by status and priority, overdue tasks, and completion percentage.

        Include automated unit and integration tests using an isolated temporary
        database. Provide clear handling for invalid IDs, malformed requests,
        duplicate or invalid data, database errors, and unsupported state
        transitions.

        Use FastAPI, Pydantic, SQLite, and a uv-managed Python project. Declare
        an application entry point so the service can be started with
        uv run <entry-point>. Include a concise README with installation
        instructions, API examples, expected responses, error behavior, and all
        commands required to run and verify the application.
        """.strip()

        run_new_workflow(request)

    print("\nGraph completed.")


def run_new_workflow(request: str) -> None:
    workflow_run = create_workflow_run(request)

    config = build_workflow_config(workflow_run.thread_id)

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


def resume_workflow(thread_id: str) -> None:
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

    config = build_workflow_config(workflow_run.thread_id)

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


if __name__ == "__main__":
    run()
