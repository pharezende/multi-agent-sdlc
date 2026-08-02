from multi_agent_sdlc.llm.config import MODEL_CONFIG
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS


base_coder_model = create_chat_model(
    MODEL_CONFIG.coder,
)

coder_llm = base_coder_model.bind_tools(CODER_TOOLS, strict=True).with_retry(
    stop_after_attempt=3
)
