from enum import StrEnum

# Free models from OpenRouter
# Paid models from OpenRouter to be added to the .env file


class ModelId(StrEnum):
    NVIDIA_NEMOTRON_3_ULTRA_FREE = "nvidia/nemotron-3-ultra-550b-a55b:free"
    INCLUSION_AI_LING_3_FLASH_FREE = "inclusionai/ling-3.0-flash:free"
