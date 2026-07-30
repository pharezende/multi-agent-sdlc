from multi_agent_sdlc.models import DevelopmentPlan
from multi_agent_sdlc.llm.config import MODEL_CONFIG
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.tools.coder.registry import CODER_TOOLS


base_coder_model = create_chat_model(
    MODEL_CONFIG.planner,
)

planner_llm = base_coder_model.with_structured_output(DevelopmentPlan).with_retry(
    stop_after_attempt=3
)
