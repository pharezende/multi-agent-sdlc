from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver

CHECKPOINT_DATABASE_PATH = Path(".data/checkpoints.sqlite")


def get_thread_id(config: RunnableConfig) -> str:
    configurable = config.get("configurable")

    if configurable is None:
        raise ValueError("RunnableConfig must contain 'configurable'.")

    thread_id = configurable.get("thread_id")

    if not isinstance(thread_id, str) or not thread_id:
        raise ValueError("RunnableConfig must contain a non-empty 'thread_id'.")

    return thread_id


@contextmanager
def create_checkpointer() -> Iterator[SqliteSaver]:
    CHECKPOINT_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SqliteSaver.from_conn_string(str(CHECKPOINT_DATABASE_PATH)) as checkpointer:
        yield checkpointer


def build_workflow_config(
    thread_id: str,
    configurable: dict[str, object] | None = None,
    checkpoint_id: str | None = None,
) -> RunnableConfig:
    configurable_values: dict[str, object] = {
        "thread_id": thread_id,
    }

    if configurable is not None:
        configurable_values.update(configurable)

    if checkpoint_id is not None:
        configurable_values["checkpoint_id"] = checkpoint_id

    return {
        "configurable": configurable_values,
    }
