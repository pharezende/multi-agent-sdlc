from typing import TypedDict
from enum import StrEnum


class OpenRouterProviderConfig(TypedDict):
    only: list[str]
    allow_fallbacks: bool


class ModelId(StrEnum):
    NVIDIA_NEMOTRON_3_ULTRA_FREE = "nvidia/nemotron-3-ultra-550b-a55b:free"
    INCLUSION_AI_LING_3_FLASH_FREE = "inclusionai/ling-3.0-flash:free"
    DEEPSEEK_V4_FLASH_0731_PAID = "deepseek/deepseek-v4-flash-0731"


MODEL_PROVIDER_CONFIG: dict[
    str,
    OpenRouterProviderConfig,
] = {
    ModelId.DEEPSEEK_V4_FLASH_0731_PAID: {
        "only": ["deepinfra/fp4", "novita/fp8"],
        "allow_fallbacks": True,
    },
}
