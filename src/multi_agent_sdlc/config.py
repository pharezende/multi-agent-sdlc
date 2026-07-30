from typing import Any
from typing import Mapping
import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter
from langchain_core.language_models.chat_models import BaseChatModel


load_dotenv(override=True)

DOC_PLAN_PATH = os.getenv("DOC_PLAN_PATH")
SANDBOX_ROOT = os.getenv("SANDBOX_ROOT")


def create_llm(
    model: str = "nvidia/nemotron-3-ultra-550b-a55b:free",
    reasoning: Mapping[str, Any] = {"effort": "high"},
) -> ChatOpenRouter:
    return ChatOpenRouter(
        model=model,
        reasoning=reasoning,
        timeout=180000,
        max_retries=0,
        # model="inclusionai/ling-3.0-flash:free",
    )
