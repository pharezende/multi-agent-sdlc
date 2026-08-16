from multi_agent_sdlc.workflow.graph import generate_diagram
from pydantic import BaseModel
from multi_agent_sdlc.presentation.terminal_verification_block_review import (
    collect_verification_block_review,
)
from typing import Any
from langgraph.types import Interrupt
from langchain_core.runnables import RunnableConfig
from langgraph.types import Command

from multi_agent_sdlc.presentation.terminal_plan_review import (
    collect_plan_review_decision,
)

from .checkpointing import build_workflow_config, create_checkpointer
from .graph import build_graph
from .run_repository import (
    WorkflowRun,
    WorkflowRunStatus,
    create_workflow_run,
    get_workflow_run,
    update_workflow_run_status,
)
from .state import build_initial_state


def run_new_workflow(
    request: str,
    configurable: dict[str, Any],
) -> None:
    workflow_run = create_workflow_run(request)

    config = build_workflow_config(
        workflow_run.thread_id,
        configurable,
    )
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


def resume_workflow(
    thread_id: str,
    checkpoint_id: str,
    configurable: dict[str, Any],
) -> None:
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

    config = build_workflow_config(workflow_run.thread_id, configurable, checkpoint_id)

    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)
        snapshot = graph.get_state(config)

        if snapshot.interrupts:
            interrupt = snapshot.interrupts[0]

            if not isinstance(interrupt, Interrupt):
                raise TypeError(
                    f"Expected Interrupt, got " f"{type(interrupt).__name__}."
                )
            result = _resume_interrupt(
                graph,
                interrupt,
                workflow_run,
                config,
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
    result: dict[str, object],
    workflow_run: WorkflowRun,
    config: RunnableConfig,
) -> None:
    interrupts = result.get("__interrupt__", ())

    while isinstance(interrupts, tuple) and interrupts:
        interrupt = interrupts[0]

        if not isinstance(interrupt, Interrupt):
            raise TypeError(f"Expected Interrupt, got " f"{type(interrupt).__name__}.")

        result = _resume_interrupt(
            graph,
            interrupt,
            workflow_run,
            config,
        )

        interrupts = result.get("__interrupt__", ())

    snapshot = graph.get_state(config)

    if snapshot.next:
        raise RuntimeError(
            f"Workflow run {workflow_run.thread_id} stopped with "
            f"pending nodes: {snapshot.next!r}."
        )

    update_workflow_run_status(
        workflow_run.thread_id,
        WorkflowRunStatus.COMPLETED,
    )

    print("\nWorkflow execution completed.")


def _collect_interrupt_response(
    interrupt_value: dict[str, Any],
) -> BaseModel:
    interrupt_type = interrupt_value.get("type")
    content = interrupt_value.get("content")
    if not isinstance(interrupt_type, str):
        raise ValueError("Interrupt type is missing or invalid.")

    if not isinstance(content, str):
        raise ValueError("Interrupt content is missing or invalid.")

    print()
    print(content)
    if interrupt_type == "plan_review":
        print("\nGraph paused for plan review.")
        return collect_plan_review_decision()

    if interrupt_type == "verification_block_review":
        print("\nGraph paused because verification is blocked.")
        return collect_verification_block_review()

    raise ValueError(f"Unsupported interrupt type: {interrupt_type!r}")


def _resume_interrupt(
    graph,
    interrupt: Interrupt,
    workflow_run: WorkflowRun,
    config: RunnableConfig,
) -> dict[str, object]:
    update_workflow_run_status(
        workflow_run.thread_id,
        WorkflowRunStatus.INTERRUPTED,
    )

    response = _collect_interrupt_response(interrupt.value)

    update_workflow_run_status(
        workflow_run.thread_id,
        WorkflowRunStatus.RUNNING,
    )

    return graph.invoke(
        Command(
            resume=response.model_dump(mode="json"),
        ),
        config=config,
    )
