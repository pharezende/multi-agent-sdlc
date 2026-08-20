from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

from multi_agent_sdlc.agents.coder.models import CoderCycle, CoderSummary
from multi_agent_sdlc.agents.planner.models import DevelopmentPlan, RiskLevel
from multi_agent_sdlc.agents.reviewer.models import ReviewerSummary
from multi_agent_sdlc.agents.tester.model import TesterCycle, TesterSummary, VerificationType
from multi_agent_sdlc.deployment.models import (
    ApplicationVerificationResult,
    DeploymentResult,
)
from multi_agent_sdlc.tools.tester.model import ProjectVerificationResult
from multi_agent_sdlc.workflow.models import (
    DevelopmentStatus,
    PlanReviewDecision,
    PlanReviewStatus,
    ReviewCycle,
    ReviewStatus,
    VerificationBlockReview,
    VerificationStatus,
)

CHECKPOINT_SERDE = JsonPlusSerializer(
    allowed_msgpack_modules=[
        DevelopmentPlan,
        CoderSummary,
        CoderCycle,
        TesterSummary,
        TesterCycle,
        ProjectVerificationResult,
        ReviewerSummary,
        ReviewCycle,
        PlanReviewDecision,
        VerificationBlockReview,
        DeploymentResult,
        ApplicationVerificationResult,
        RiskLevel,
        VerificationType,
        PlanReviewStatus,
        DevelopmentStatus,
        VerificationStatus,
        ReviewStatus,
    ],
)


CHECKPOINT_DATABASE_PATH = Path(".data/checkpoints.sqlite")


def get_thread_id(config: RunnableConfig) -> str:
    configurable = config.get("configurable")

    if configurable is None:
        raise ValueError("RunnableConfig must contain 'configurable'.")

    thread_id = configurable.get("thread_id")

    if not isinstance(thread_id, str) or not thread_id:
        raise ValueError("RunnableConfig must contain a non-empty 'thread_id'.")

    return thread_id


@contextmanager
def create_checkpointer() -> Iterator[SqliteSaver]:
    CHECKPOINT_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with SqliteSaver.from_conn_string(str(CHECKPOINT_DATABASE_PATH)) as checkpointer:
        checkpointer.serde = CHECKPOINT_SERDE

        yield checkpointer


def build_workflow_config(
    thread_id: str,
    configurable: dict[str, object] | None = None,
    checkpoint_id: str | None = None,
) -> RunnableConfig:
    configurable_values: dict[str, object] = {
        "thread_id": thread_id,
    }

    if configurable is not None:
        configurable_values.update(configurable)

    if checkpoint_id is not None:
        configurable_values["checkpoint_id"] = checkpoint_id

    return {
        "configurable": configurable_values,
    }
