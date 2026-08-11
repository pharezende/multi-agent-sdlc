from multi_agent_sdlc.workflow.graph import build_graph
from multi_agent_sdlc.workflow.checkpointing import (
    build_workflow_config,
    create_checkpointer,
)

THREAD_ID = "7f5814dc-36b3-4686-afcb-43307f18f7b5"
CHECKPOINT_ID = "1f195c98-7e49-627b-809c-d222b46cc3c9"


def main() -> None:
    with create_checkpointer() as checkpointer:
        graph = build_graph(checkpointer)

        # Base configuration used to retrieve the thread history.
        thread_config = build_workflow_config(THREAD_ID)

        history = list(graph.get_state_history(thread_config))

        print("Available checkpoints:\n")

        for snapshot in history:
            configurable = snapshot.config.get("configurable", {})
            checkpoint_id = configurable.get("checkpoint_id")

            print(f"checkpoint_id={checkpoint_id} " f"next={snapshot.next}")

        # Find the exact checkpoint selected for recovery.
        checkpoint = next(
            (
                snapshot
                for snapshot in history
                if snapshot.config.get("configurable", {}).get("checkpoint_id")
                == CHECKPOINT_ID
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
            f"\n  next: {checkpoint.next}"
        )

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
