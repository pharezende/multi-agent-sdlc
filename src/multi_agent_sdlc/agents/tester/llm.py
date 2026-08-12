from multi_agent_sdlc.llm.config import load_model_config
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG
from multi_agent_sdlc.tools.tester.registry import TESTER_TOOLS


def create_tester_llm():
    model = load_model_config().tester

    base_model = create_chat_model(
        model,
        provider=MODEL_PROVIDER_CONFIG.get(model),
    )

    return base_model.bind_tools(
        TESTER_TOOLS,
        tool_choice="required",
        strict=True,
    ).with_retry(stop_after_attempt=3)
