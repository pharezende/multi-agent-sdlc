from multi_agent_sdlc.agents.tester.messages import (
    build_tester_verification_retry_message,
)
from multi_agent_sdlc.workflow.models import VerificationBlockDecision
from multi_agent_sdlc.workflow.models import ReviewStatus
from multi_agent_sdlc.agents.reviewer.messages import build_reviewer_rereview_messages
from multi_agent_sdlc.agents.reviewer.messages import build_reviewer_initial_messages
import json

from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from multi_agent_sdlc.agents.coder.context import (
    build_coder_implementation_context,
    build_coder_repair_context,
)
from multi_agent_sdlc.agents.tester.messages import (
    build_tester_initial_messages,
    build_tester_retest_messages,
)
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_CHAT_PROMPT_TEMPLATE,
    CODER_REPAIR_CHAT_PROMPT_TEMPLATE,
    CODER_SYSTEM_RULES,
)
from multi_agent_sdlc.agents.planner.prompt import (
    PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE,
)
from multi_agent_sdlc.presentation.plan_formatter import format_plan
from multi_agent_sdlc.presentation.plan_pdf import export_plan_to_pdf
from multi_agent_sdlc.system.path_utils import create_project_directory

from .checkpointing import get_thread_id
from .models import DevelopmentStatus, PlanReviewStatus, VerificationStatus
from .run_repository import update_workflow_project_directory
from .state import DevState


def prepare_plan_review_node(
    state: DevState,
) -> dict[str, object]:
    plan = state["plan"]

    if plan is None:
        raise ValueError("Cannot prepare review for a missing plan.")

    return {
        "plan_review_status": PlanReviewStatus.AWAITING_REVIEW,
        "plan_review_decision": None,
        "plan_review_content": format_plan(plan),
    }


def prepare_planner_revision_node(
    state: DevState,
) -> dict[str, list[HumanMessage]]:
    review_decision = state["plan_review_decision"]

    if review_decision is None:
        raise ValueError("Plan review decision is missing.")

    revision_prompt = PLANNER_REVISION_HUMAN_PROMPT_TEMPLATE.format(
        human_feedback=review_decision.feedback,
    )

    return {
        "planner_messages": [
            HumanMessage(content=revision_prompt),
        ],
    }


def prepare_coder_implementation_node(
    state: DevState,
    config: RunnableConfig,
) -> dict[str, object]:
    plan = state["plan"]
    plan_review_content = state["plan_review_content"]

    if plan is None:
        raise ValueError("Plan cannot be None.")

    if plan_review_content is None:
        raise ValueError("Plan review content cannot be None.")

    project_directory = create_project_directory(plan.project_id)

    update_workflow_project_directory(
        get_thread_id(config),
        str(project_directory),
    )

    export_plan_to_pdf(
        text=plan_review_content,
        output_path=project_directory / "development_plan.pdf",
    )

    coder_context = build_coder_implementation_context(
        state=state,
    )

    prompt_value = CODER_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_rules": CODER_SYSTEM_RULES,
            "coder_execution_input": json.dumps(
                coder_context,
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "project_directory": project_directory.resolve(),
        "development_status": DevelopmentStatus.IMPLEMENTING,
        "coder_invalid_response_count": 0,
        "coder_messages": prompt_value.to_messages(),
    }


def prepare_tester_node(
    state: DevState,
) -> dict[str, object]:

    verification_block_review = state["verification_block_review"]

    if (
        verification_block_review is not None
        and verification_block_review.decision == VerificationBlockDecision.RETRY
    ):
        messages = build_tester_verification_retry_message(state)

    else:
        coder_summary = state["current_coder_summary"]

        if coder_summary is None:
            raise ValueError("Cannot prepare the Tester without a Coder summary.")

        existing_messages = state.get("tester_messages", [])

        if existing_messages:
            messages = [
                build_tester_retest_messages(state),
            ]
        else:
            messages = build_tester_initial_messages(state)

    return {
        "verification_status": VerificationStatus.VERIFYING,
        "tester_messages": messages,
        "current_project_verification_result": None,
    }


def prepare_coder_repair_node(
    state: DevState,
) -> dict[str, object]:
    prompt_value = CODER_REPAIR_CHAT_PROMPT_TEMPLATE.invoke(
        {
            "coder_repair_input": json.dumps(
                build_coder_repair_context(state),
                indent=2,
                ensure_ascii=False,
            ),
        }
    )

    return {
        "development_status": DevelopmentStatus.REPAIRING,
        "coder_messages": prompt_value.to_messages(),
        "current_coder_summary": None,
    }


def prepare_reviewer_node(state: DevState) -> dict[str, object]:
    reviewer_history = state.get("reviewer_summary_history", [])

    if not reviewer_history:
        reviewer_messages = build_reviewer_initial_messages(state)
    else:
        reviewer_messages = [
            *state["reviewer_messages"],
            *build_reviewer_rereview_messages(state),
        ]

    return {
        "reviewer_messages": reviewer_messages,
        "review_status": ReviewStatus.REVIEWING,
        "current_reviewer_summary": None,
    }
