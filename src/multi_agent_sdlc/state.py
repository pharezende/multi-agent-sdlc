from multi_agent_sdlc.models import PlanReviewDecision
from multi_agent_sdlc.models import PlanReviewStatus
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
    plan: DevelopmentPlan | None
    project_directory: str | None
    planner_messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]
    plan_review_status: PlanReviewStatus
    plan_review_decision: PlanReviewDecision | None
    plan_review_content: str | None

    coder_messages: Annotated[list[BaseMessage], add_messages]
    coder_status: CoderStatus | None
    current_coder_summary: CoderSummary | None
    coder_summary_history: Annotated[
        list[ImplementationCycle],
        add,
    ]

    tester_messages: Annotated[list[BaseMessage], add_messages]
    tester_status: TesterStatus | None
    current_tester_summary: TesterSummary | None
    verification_history: Annotated[
        list[VerificationCycle],
        add,
    ]

    current_project_verification_result: ProjectVerificationResult | None
