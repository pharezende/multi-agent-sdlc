from langchain_core.runnables import RunnableConfig


def get_thread_id(config: RunnableConfig) -> str:
    configurable = config.get("configurable")

    if configurable is None:
        raise ValueError("RunnableConfig must contain 'configurable'.")

    thread_id = configurable.get("thread_id")

    if not isinstance(thread_id, str) or not thread_id:
        raise ValueError("RunnableConfig must contain a non-empty 'thread_id'.")

    return thread_id
