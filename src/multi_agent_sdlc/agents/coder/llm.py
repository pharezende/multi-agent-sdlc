from multi_agent_sdlc.llm.config import load_model_config
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS


def create_coder_llm():
    model = load_model_config().coder

    base_coder_model = create_chat_model(
        model,
        provider=MODEL_PROVIDER_CONFIG.get(model),
    )

    return base_coder_model.bind_tools(
        CODER_TOOLS, tool_choice="required", strict=True
    ).with_retry(stop_after_attempt=3)
