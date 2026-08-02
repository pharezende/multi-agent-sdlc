from multi_agent_sdlc.models import CoderStatus
from multi_agent_sdlc.models import TesterStatus
from multi_agent_sdlc.models import CoderMode
from multi_agent_sdlc.models import ImplementationCycle
from multi_agent_sdlc.models import VerificationCycle
from multi_agent_sdlc.models import TesterSummary
from multi_agent_sdlc.models import CoderSummary
from langgraph.graph import add_messages
from operator import add
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
    coder_status: NotRequired[CoderStatus]
    current_coder_summary: NotRequired[CoderSummary]
    coder_summary_history: Annotated[
        list[ImplementationCycle],
        add,
    ]
    tester_status: NotRequired[TesterStatus]
    tester_messages: Annotated[list[BaseMessage], add_messages]
    current_tester_summary: TesterSummary | None
    verification_history: Annotated[
        list[VerificationCycle],
        add,
    ]
