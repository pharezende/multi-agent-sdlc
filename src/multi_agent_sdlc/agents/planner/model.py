from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG
from multi_agent_sdlc.llm.config import MODEL_CONFIG
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.models import DevelopmentPlan

base_planner_model = create_chat_model(
    MODEL_CONFIG.planner, provider=MODEL_PROVIDER_CONFIG.get(MODEL_CONFIG.planner)
)


planner_llm = base_planner_model.with_structured_output(
    DevelopmentPlan,
    method="json_schema",
    strict=True,
).with_retry(
    stop_after_attempt=3,
)
