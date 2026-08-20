from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.llm.config import load_model_config
from multi_agent_sdlc.llm.factory import create_chat_model
from multi_agent_sdlc.llm.models import MODEL_PROVIDER_CONFIG


def create_planner_llm():
    model = load_model_config().planner

    base_planner_model = create_chat_model(
        model,
        provider=MODEL_PROVIDER_CONFIG.get(model),
    )

    return base_planner_model.with_structured_output(
        DevelopmentPlan,
        method="json_schema",
        strict=True,
    ).with_retry(
        stop_after_attempt=3,
    )
