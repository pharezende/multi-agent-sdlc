from multi_agent_sdlc.agents.tester.model import TesterCycle
from multi_agent_sdlc.agents.tester.model import TesterSummary
from .models import VerificationStatus
from multi_agent_sdlc.agents.coder.models import CoderCycle
from multi_agent_sdlc.agents.coder.models import CoderSummary
from .models import DevelopmentStatus
from .models import PlanReviewDecision
from .models import PlanReviewStatus
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from operator import add
from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from multi_agent_sdlc.tools.tester.validation import ProjectVerificationResult


class DevState(TypedDict):
    request: str

    plan: DevelopmentPlan | None
    planner_messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    project_directory: str | None
    coder_messages: Annotated[list[BaseMessage], add_messages]
    current_coder_summary: CoderSummary | None
    coder_invalid_response_count: int  # Need for the tester as well.
    coder_summary_history: Annotated[
        list[CoderCycle],
        add,
    ]

    tester_messages: Annotated[list[BaseMessage], add_messages]
    current_tester_summary: TesterSummary | None
    tester_summary_history: Annotated[
        list[TesterCycle],
        add,
    ]

    current_project_verification_result: ProjectVerificationResult | None

    plan_review_status: PlanReviewStatus
    plan_review_decision: PlanReviewDecision | None
    plan_review_content: str | None
    development_status: DevelopmentStatus | None
    verification_status: VerificationStatus | None


def build_initial_state(request: str) -> DevState:
    return {
        "request": request,
        "plan": None,
        "project_directory": None,
        "plan_review_status": PlanReviewStatus.NOT_STARTED,
        "plan_review_decision": None,
        "plan_review_content": None,
        "planner_messages": [],
        "coder_messages": [],
        "development_status": DevelopmentStatus.NOT_STARTED,
        "current_coder_summary": None,
        "coder_invalid_response_count": 0,
        "coder_summary_history": [],
        "tester_messages": [],
        "verification_status": VerificationStatus.NOT_STARTED,
        "current_tester_summary": None,
        "tester_summary_history": [],
        "current_project_verification_result": None,
    }
