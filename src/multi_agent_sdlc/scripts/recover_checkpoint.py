from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from langgraph.types import StateSnapshot

from multi_agent_sdlc.workflow.checkpointing import (
    build_workflow_config,
    create_checkpointer,
)
from multi_agent_sdlc.workflow.graph import build_graph

load_dotenv(override=True)

THREAD_ID = "7b02e2f4-1ffb-41ba-9d84-dc03c179e192"
CHECKPOINT_ID = ""


def _get_configurable_value(
    config: RunnableConfig | None,
    key: str,
) -> object | None:
    if config is None:
        return None

    return config.get("configurable", {}).get(key)


def _get_checkpoint_id(
    config: RunnableConfig | None,
) -> str | None:
    checkpoint_id = _get_configurable_value(
        config,
        "checkpoint_id",
    )

    return checkpoint_id if isinstance(checkpoint_id, str) else None


def _get_checkpoint_node(
    snapshot: StateSnapshot,
) -> str:
    metadata = snapshot.metadata or {}
    writes = metadata.get("writes")

    if isinstance(writes, dict) and writes:
        return ", ".join(writes)

    if snapshot.tasks:
        return ", ".join(task.name for task in snapshot.tasks)

    return "-"


def _get_task_names(
    snapshot: StateSnapshot,
) -> list[str]:
    return [task.name for task in snapshot.tasks]


def _format_values(
    values: list[str],
) -> str:
    if not values:
        return "-"

    return ", ".join(values)


def _find_forks(
    history: list[StateSnapshot],
) -> dict[str, list[str]]:
    children_by_parent: dict[str, list[str]] = {}

    for snapshot in history:
        checkpoint_id = _get_checkpoint_id(snapshot.config)
        parent_checkpoint_id = _get_checkpoint_id(snapshot.parent_config)

        if checkpoint_id is None or parent_checkpoint_id is None:
            continue

        children_by_parent.setdefault(
            parent_checkpoint_id,
            [],
        ).append(checkpoint_id)

    return {
        parent: children
        for parent, children in children_by_parent.items()
        if len(children) > 1
    }


def _print_selected_checkpoint(
    checkpoint: StateSnapshot,
) -> None:
    checkpoint_id = _get_checkpoint_id(checkpoint.config)
    parent_checkpoint_id = _get_checkpoint_id(checkpoint.parent_config)

    metadata = checkpoint.metadata or {}
    step = metadata.get("step")

    print("\nSelected checkpoint:")
    print(f"  id: {checkpoint_id}")
    print(f"  parent: {parent_checkpoint_id}")
    print(f"  node: {_get_checkpoint_node(checkpoint)}")
    print(f"  step: {step}")
    print(f"  created_at: {checkpoint.created_at}")
    print(f"  next: {checkpoint.next}")
    print(f"  interrupted: " f"{bool(checkpoint.interrupts)}")
    print(f"  has_pending_nodes: " f"{bool(checkpoint.next)}")
    print("  tasks: " f"{_format_values(_get_task_names(checkpoint))}")


def main() -> None:
    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        thread_config = build_workflow_config(THREAD_ID)

        history = list(graph.get_state_history(thread_config))

        if not history:
            raise RuntimeError(
                f"No checkpoints were found for thread " f"{THREAD_ID!r}."
            )

        forks = _find_forks(history)

        print(f"Thread: {THREAD_ID}")
        print(f"Total checkpoints: {len(history)}")
        print("\nAvailable checkpoints:\n")

        for snapshot in history:
            checkpoint_id = _get_checkpoint_id(snapshot.config)
            parent_checkpoint_id = _get_checkpoint_id(snapshot.parent_config)
            node = _get_checkpoint_node(snapshot)

            markers: list[str] = []

            if checkpoint_id == CHECKPOINT_ID:
                markers.append("SELECTED")

            if checkpoint_id in forks:
                markers.append(f"FORK POINT " f"({len(forks[checkpoint_id])} branches)")

            if snapshot.interrupts:
                markers.append("INTERRUPTED")

            marker_text = f" <-- {', '.join(markers)}" if markers else ""

            print(
                f"checkpoint_id={checkpoint_id} "
                f"parent={parent_checkpoint_id} "
                f"node={node}"
                f"{marker_text}"
            )

        if forks:
            print("\nDetected forks:\n")

            for (
                parent_checkpoint_id,
                children,
            ) in forks.items():
                print(f"Fork point: " f"{parent_checkpoint_id}")

                for child_checkpoint_id in children:
                    print(f"  └─> {child_checkpoint_id}")

                print()
        else:
            print("\nNo checkpoint forks detected.")

        selected_checkpoint = next(
            (
                snapshot
                for snapshot in history
                if _get_checkpoint_id(snapshot.config) == CHECKPOINT_ID
            ),
            None,
        )

        if selected_checkpoint is None:
            print(
                f"\nSelected checkpoint "
                f"{CHECKPOINT_ID!r} was not found "
                f"in thread {THREAD_ID!r}."
            )
            return

        _print_selected_checkpoint(selected_checkpoint)


if __name__ == "__main__":
    main()
