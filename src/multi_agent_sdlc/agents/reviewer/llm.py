from multi_agent_sdlc.tools.reviewer.registry import REVIEWER_TOOLS
from multi_agent_sdlc.llm.config import load_model_config
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG


def create_reviewer_llm():
    model = load_model_config().reviewer

    base_model = create_chat_model(
        model,
        provider=MODEL_PROVIDER_CONFIG.get(model),
    )

    return base_model.bind_tools(
        REVIEWER_TOOLS,
        tool_choice="required",
        strict=True,
    ).with_retry(stop_after_attempt=3)
