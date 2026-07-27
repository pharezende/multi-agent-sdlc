from multi_agent_sdlc.config import SANDBOX_ROOT
from multi_agent_sdlc.config import DOC_PLAN_PATH
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from .state import DevState
from .prompts.planner import PLANNER_SYSTEM_PROMPT
from .formatting.plan import format_plan
from .exporter.pdf import export_plan_to_pdf
from .models import DevelopmentPlan
from pathlib import Path
from re import fullmatch


def create_project_directory(project_id: str) -> Path:
    if not fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("project_id must use lowercase kebab-case.")

    project_directory = Path(SANDBOX_ROOT) / project_id
    project_directory.mkdir(parents=True, exist_ok=True)

    return project_directory


def create_planner_node(llm: BaseChatModel):

    structured_llm = llm.with_structured_output(DevelopmentPlan).with_retry(
        retry_if_exception_type=(Exception,),
        stop_after_attempt=3,
    )

    def planner_node(state: DevState) -> DevState:
        user_request = state["request"]
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_PROMPT),
            HumanMessage(content=user_request),
        ]

        plan = structured_llm.invoke(messages)

        project_directory = create_project_directory(plan.project_id)

        plan_text = format_plan(plan)

        export_plan_to_pdf(
            text=plan_text,
            output_path=project_directory / "development-plan.pdf",
        )

        return {
            "request": user_request,
            "plan": plan,
        }

    return planner_node
