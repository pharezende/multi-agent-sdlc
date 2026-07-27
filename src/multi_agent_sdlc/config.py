import os
from dotenv import load_dotenv
from langchain_openrouter import ChatOpenRouter


load_dotenv(override=True)

DOC_PLAN_PATH = os.getenv("DOC_PLAN_PATH")
SANDBOX_ROOT = os.getenv("SANDBOX_ROOT")


def create_llm() -> ChatOpenRouter:
    return ChatOpenRouter(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
    )
