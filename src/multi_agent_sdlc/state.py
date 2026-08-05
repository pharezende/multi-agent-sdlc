from operator import add
from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from multi_agent_sdlc.models import (
    CoderStatus,
    CoderSummary,
    ImplementationCycle,
    TesterStatus,
    TesterSummary,
    VerificationCycle,
)
from multi_agent_sdlc.tools.tester.validation import ProjectVerificationResult

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
    current_project_verification_result: NotRequired[ProjectVerificationResult | None]
