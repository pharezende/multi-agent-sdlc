from typing_extensions import List
from langchain_core.runnables import RunnableConfig
from langgraph.types import StateSnapshot
from multi_agent_sdlc.workflow.graph import build_graph
from multi_agent_sdlc.workflow.checkpointing import (
    build_workflow_config,
    create_checkpointer,
)
from dotenv import load_dotenv

load_dotenv(override=True)

THREAD_ID = "7f5814dc-36b3-4686-afcb-43307f18f7b5"
CHECKPOINT_ID = "1f196743-bfa5-61b8-80ad-33889d39e792"


def _get_checkpoint_id(
    config: RunnableConfig | None,
) -> str | None:
    if config is None:
        return None

    checkpoint_id = config.get("configurable", {}).get("checkpoint_id")

    return checkpoint_id if isinstance(checkpoint_id, str) else None


def _find_forks(
    history: List[StateSnapshot],
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


def main() -> None:
    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        # Base configuration used to retrieve the thread history.
        thread_config = build_workflow_config(THREAD_ID)

        history = list(graph.get_state_history(thread_config))

        forks = _find_forks(history)

        print("Available checkpoints:\n")

        for snapshot in history:
            checkpoint_id = _get_checkpoint_id(snapshot.config)
            parent_checkpoint_id = _get_checkpoint_id(snapshot.parent_config)

            markers: list[str] = []

            if checkpoint_id == CHECKPOINT_ID:
                markers.append("selected for recovery")

            if checkpoint_id in forks:
                markers.append(f"FORK POINT ({len(forks[checkpoint_id])} branches)")

            marker_text = f" <-- {', '.join(markers)}" if markers else ""

            print(
                f"checkpoint_id={checkpoint_id} "
                f"parent_checkpoint_id={parent_checkpoint_id} "
                f"next={snapshot.next}"
                f"{marker_text}"
            )

        if forks:
            print("\nDetected forks:\n")

            for parent_checkpoint_id, children in forks.items():
                print(f"Fork point: {parent_checkpoint_id}")

                for child_checkpoint_id in children:
                    print(f"  └─> {child_checkpoint_id}")

                print()
        else:
            print("\nNo checkpoint forks detected.")

        # Find the exact checkpoint selected for recovery.
        checkpoint = next(
            (
                snapshot
                for snapshot in history
                if _get_checkpoint_id(snapshot.config) == CHECKPOINT_ID
            ),
            None,
        )

        if checkpoint is None:
            raise RuntimeError(
                f"Checkpoint {CHECKPOINT_ID!r} was not found "
                f"for thread {THREAD_ID!r}."
            )

        print(
            "\nResuming from checkpoint:"
            f"\n  id: {CHECKPOINT_ID}"
            f"\n  parent: "
            f"{_get_checkpoint_id(checkpoint.parent_config)}"
            f"\n  next: {checkpoint.next}"
        )

        if CHECKPOINT_ID in forks:
            print("\nWARNING: The selected checkpoint is already " "a fork point.")

            print("Existing branches:")

            for child_checkpoint_id in forks[CHECKPOINT_ID]:
                print(f"  - {child_checkpoint_id}")

        if not checkpoint.next:
            raise RuntimeError(
                "The selected checkpoint has no pending nodes to execute."
            )

        # Replay from this historical checkpoint.
        result = graph.invoke(
            None,
            config=checkpoint.config,
        )

        print("\nWorkflow resumed successfully.")
        print(result)


if __name__ == "__main__":
    main()
