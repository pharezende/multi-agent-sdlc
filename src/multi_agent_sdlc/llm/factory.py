from langchain_openrouter import ChatOpenRouter


def create_chat_model(
    model: str,
    timeout_seconds: int = 180000,  # ms
    max_retries: int = 0,
    provider=None,
) -> ChatOpenRouter:
    return ChatOpenRouter(
        model=model,
        timeout=timeout_seconds,  # not working
        max_retries=max_retries,
        openrouter_provider=provider,
    )
