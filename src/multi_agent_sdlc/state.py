from multi_agent_sdlc.models import CoderSummary
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import Annotated
from typing import NotRequired
from typing import TypedDict
from .models import DevelopmentPlan


class DevState(TypedDict):
    request: str
    plan: NotRequired[DevelopmentPlan]
    project_directory: NotRequired[str]
    coder_messages: Annotated[
        list[BaseMessage], add_messages
    ]  # Reducer state field. Otherwise replaces the previous value.
    coder_summary: NotRequired[CoderSummary]
