from langchain_openrouter import ChatOpenRouter

from multi_agent_sdlc.llm.models import ModelId


def create_chat_model(
    model: ModelId,
    timeout_seconds: float = 180000,  # ms
    max_retries: int = 0,
) -> ChatOpenRouter:
    return ChatOpenRouter(
        model=model.value,
        timeout=timeout_seconds,  # not working
        max_retries=max_retries,
    )
