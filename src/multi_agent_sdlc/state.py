from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage
from typing import Annotated
from typing import NotRequired
from typing import Optional, TypedDict
from .models import DevelopmentPlan


class DevState(TypedDict):
    request: str
    plan: Optional[DevelopmentPlan]
    project_directory: NotRequired[str]
    coder_messages: Annotated[list[BaseMessage], add_messages]
