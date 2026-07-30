from multi_agent_sdlc.config import create_llm
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS


base_coder_model = create_llm()

coder_llm = base_coder_model.bind_tools(CODER_TOOLS).with_retry(stop_after_attempt=3)
