import json

from langchain_core.runnables import RunnableConfig

from multi_agent_sdlc.agents.coder.context import (
    build_coder_implementation_context,
    build_coder_repair_context,
)
from multi_agent_sdlc.agents.coder.prompt import (
    CODER_CHAT_PROMPT_TEMPLATE,
    CODER_REPAIR_CHAT_PROMPT_TEMPLATE,
    CODER_SYSTEM_RULES,
)
from multi_agent_sdlc.presentation.plan_markdown import export_plan_to_markdown
from multi_agent_sdlc.system.path_utils import create_project_directory
from multi_agent_sdlc.workflow.checkpointing import get_thread_id
from multi_agent_sdlc.workflow.models import DevelopmentStatus
from multi_agent_sdlc.workflow.run_repository import update_workflow_project_directory
from multi_agent_sdlc.workflow.state import DevState


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

    export_plan_to_markdown(
        plan=plan,
        output_path=project_directory / "development_plan.md",
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
