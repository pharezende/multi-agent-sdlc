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
    checkpoint_id: str | None,
    configurable: dict[str, Any],
) -> None:
    workflow_run = _get_resumable_workflow_run(thread_id)

    checkpoint_config = build_workflow_config(
        workflow_run.thread_id,
        configurable,
        checkpoint_id,
    )

    thread_config = build_workflow_config(
        workflow_run.thread_id,
        configurable,
    )

    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        snapshot = graph.get_state(checkpoint_config)

        if snapshot.interrupts:
            interrupt = _get_first_interrupt(
                snapshot.interrupts,
            )

            result = _resume_interrupt(
                graph,
                interrupt,
                workflow_run,
                checkpoint_config,
            )

        elif snapshot.next:
            update_workflow_run_status(
                workflow_run.thread_id,
                WorkflowRunStatus.RUNNING,
            )

            result = graph.invoke(
                None,
                config=checkpoint_config,
            )

        else:
            raise ValueError(
                f"Workflow run {workflow_run.thread_id!r} " "has no pending work."
            )

        _process_workflow_result(
            graph,
            result,
            workflow_run,
            thread_config,
        )


def _process_workflow_result(
    graph,
    result: dict[str, object],
    workflow_run: WorkflowRun,
    config: RunnableConfig,
) -> None:
    interrupts = _get_interrupts(result)

    while interrupts:
        result = _resume_interrupt(
            graph,
            interrupts[0],
            workflow_run,
            config,
        )

        interrupts = _get_interrupts(result)

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

    match interrupt_type:
        case "plan_review":
            print("\nGraph paused for plan review.")
            return collect_plan_review_decision()

        case "verification_block_review":
            print("\nGraph paused because verification is blocked.")
            return collect_verification_block_review()

        case _:
            raise ValueError(f"Unsupported interrupt type: " f"{interrupt_type!r}")


def _get_resumable_workflow_run(
    thread_id: str,
) -> WorkflowRun:
    workflow_run = get_workflow_run(thread_id)

    if workflow_run is None:
        raise ValueError(f"Workflow with thread id {thread_id!r} " "was not found.")

    if workflow_run.status in {
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.FAILED,
    }:
        raise ValueError(
            f"Workflow run {thread_id!r} cannot be resumed "
            f"because its status is {workflow_run.status!r}."
        )

    return workflow_run


def _get_interrupts(
    result: dict[str, object],
) -> list[Interrupt]:
    value = result.get("__interrupt__", ())

    if not isinstance(value, (list, tuple)):
        raise TypeError(
            "Expected __interrupt__ to be a list or tuple, "
            f"got {type(value).__name__}."
        )

    interrupts: list[Interrupt] = []

    for item in value:
        if not isinstance(item, Interrupt):
            raise TypeError(f"Expected Interrupt, got " f"{type(item).__name__}.")

        interrupts.append(item)

    return interrupts


def _get_first_interrupt(
    interrupts: tuple[Interrupt, ...],
) -> Interrupt:
    interrupt = interrupts[0]

    if not isinstance(interrupt, Interrupt):
        raise TypeError(f"Expected Interrupt, got " f"{type(interrupt).__name__}.")

    return interrupt
