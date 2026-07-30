from multi_agent_sdlc.llm.models import ModelId
from dataclasses import dataclass
import os


@dataclass(frozen=True)
class AgentModelConfig:
    planner: str
    coder: str
    tester: str
    reviewer: str


def load_model_config() -> AgentModelConfig:
    return AgentModelConfig(
        planner=os.getenv("PLANNER_MODEL", ModelId.NVIDIA_NEMOTRON_3_ULTRA_FREE),
        coder=os.getenv("CODER_MODEL", ModelId.NVIDIA_NEMOTRON_3_ULTRA_FREE),
        tester=os.getenv("TESTER_MODEL", ModelId.NVIDIA_NEMOTRON_3_ULTRA_FREE),
        reviewer=os.getenv("REVIEWER_MODEL", ModelId.NVIDIA_NEMOTRON_3_ULTRA_FREE),
    )


MODEL_CONFIG = load_model_config()
