from multi_agent_sdlc.deployment.models import DeploymentResult
from multi_agent_sdlc.deployment.models import ApplicationVerificationResult
from multi_agent_sdlc.workflow.models import ReviewCycle
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.workflow.models import ReviewStatus
from pathlib import Path
from operator import add
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

from multi_agent_sdlc.agents.coder.models import CoderCycle, CoderSummary
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan
from multi_agent_sdlc.agents.tester.model import TesterCycle, TesterSummary
from multi_agent_sdlc.tools.tester.model import ProjectVerificationResult

from .models import (
    DevelopmentStatus,
    PlanReviewDecision,
    PlanReviewStatus,
    VerificationBlockReview,
    VerificationStatus,
)


class DevState(TypedDict):
    request: str

    plan: DevelopmentPlan | None
    planner_messages: Annotated[
        list[BaseMessage],
        add_messages,
    ]

    project_directory: Path | None
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

    reviewer_messages: Annotated[list[BaseMessage], add_messages]
    current_reviewer_summary: ReviewerSummary | None
    reviewer_summary_history: Annotated[
        list[ReviewCycle],
        add,
    ]

    plan_review_status: PlanReviewStatus
    plan_review_decision: PlanReviewDecision | None
    plan_review_content: str | None
    development_status: DevelopmentStatus | None
    verification_status: VerificationStatus | None
    verification_block_review: VerificationBlockReview | None

    review_status: (
        ReviewStatus | None
    )  # I think all status will be moved to the respective Cycle later.

    deployment_result: DeploymentResult | None
    deployment_verification: ApplicationVerificationResult | None


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
        "reviewer_messages": [],
        "current_reviewer_summary": None,
        "reviewer_summary_history": [],
        "verification_block_review": None,
        "review_status": ReviewStatus.NOT_STARTED,
        "deployment_result": None,
        "deployment_verification": None,
    }
