from multi_agent_sdlc.agents.planner.prompt import PLANNER_SYSTEM_RULES
from multi_agent_sdlc.agents.planner.exporter import export_plan_to_pdf
from multi_agent_sdlc.agents.planner.formatter import format_plan
from multi_agent_sdlc.state import DevState
from multi_agent_sdlc.config import SANDBOX_ROOT
from re import fullmatch
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pathlib import Path


def create_project_directory(project_id: str) -> Path:
    "Create project folder inside 'sandbox', e.g: terminal-calculator"

    if not fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("project_id must use lowercase kebab-case.")

    project_directory = Path(SANDBOX_ROOT) / project_id
    project_directory.mkdir(parents=True, exist_ok=True)

    return project_directory


def create_planner_node(llm: BaseChatModel):
    """Create the planner node, which is responsible for planning the application requested by the user."""

    def planner_node(state: DevState) -> DevState:
        user_request = state["request"]
        messages = [
            SystemMessage(content=PLANNER_SYSTEM_RULES),
            HumanMessage(content=user_request),
        ]

        plan = llm.invoke(messages)

        project_directory = create_project_directory(plan.project_id)

        plan_text = format_plan(plan)

        export_plan_to_pdf(
            text=plan_text,
            output_path=project_directory / "development-plan.pdf",
        )

        return {
            "request": user_request,
            "plan": plan,
            "project_directory": str(project_directory),
        }

    return planner_node
