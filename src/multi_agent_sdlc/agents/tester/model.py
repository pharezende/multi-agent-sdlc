from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG
from multi_agent_sdlc.llm.config import MODEL_CONFIG
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.tools.tester.registry import TESTER_TOOLS

base_tester_model = create_chat_model(
    MODEL_CONFIG.tester, provider=MODEL_PROVIDER_CONFIG.get(MODEL_CONFIG.tester)
)

tester_llm = base_tester_model.bind_tools(
    TESTER_TOOLS, tool_choice="required", strict=True
).with_retry(stop_after_attempt=3)
