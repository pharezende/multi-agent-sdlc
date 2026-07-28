from langchain_core.messages import AIMessage
from multi_agent_sdlc.prompts.coder import CODER_PROMPT
from multi_agent_sdlc.config import SANDBOX_ROOT
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from .state import DevState
from .prompts.planner import PLANNER_SYSTEM_PROMPT
from .formatting.plan import format_plan
from .exporter.pdf import export_plan_to_pdf
from .models import DevelopmentPlan
from pathlib import Path
from re import fullmatch
import json
from typing import Any, Literal
import time
from openrouter.errors import ResponseValidationError


def create_project_directory(project_id: str) -> Path:
    "Create project folder inside 'sandbox', e.g: terminal-calculator"

    if not fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", project_id):
        raise ValueError("project_id must use lowercase kebab-case.")

    project_directory = Path(SANDBOX_ROOT) / project_id
    project_directory.mkdir(parents=True, exist_ok=True)

    return project_directory


def create_planner_node(llm: BaseChatModel):
    """Create the planner node, which is responsible for planning the application requested by the user."""

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
            "project_directory": str(project_directory),
        }

    return planner_node


def build_coder_context(state: DevState) -> dict[str, Any]:

    plan = state.get("plan")
    if plan is None:
        raise ValueError("Development plan is missing from the state.")

    project_directory = state.get("project_directory")
    if not project_directory:
        raise ValueError("Project directory is missing from the state.")

    request = state.get("request")
    if not request or not request.strip():
        raise ValueError("Development request is missing from the state.")

    return {
        "request": request,
        "project_directory": project_directory,
        "plan": plan.model_dump(mode="json"),
    }


def finalize_coder(
    state: DevState,
) -> dict[str, Any]:
    coder_messages = state.get("coder_messages", [])

    return {}


def route_after_coder(
    state: DevState,
) -> Literal[
    "coder_tools",
    "finalize_coder",
]:
    messages = state.get("coder_messages", [])

    last_message = messages[-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "coder_tools"

    return "finalize_coder"


def create_coder_node(
    llm: BaseChatModel,
    tools: list,
):
    llm_with_tools = llm.bind_tools(tools)

    def coder_node(state: DevState) -> dict:

        coder_messages = state.get("coder_messages", [])

        if not coder_messages:
            initial_messages = CODER_PROMPT.format_messages(
                coder_context=json.dumps(
                    build_coder_context(state),
                    indent=2,
                    ensure_ascii=False,
                )
            )

            response = llm_with_tools.invoke(initial_messages)

            return {
                "coder_messages": [
                    *initial_messages,
                    response,
                ],
            }

        # response = llm_with_tools.invoke(coder_messages)
        response = invoke_with_retry(
            llm_with_tools,
            coder_messages,
            max_attempts=3,
        )

        return {
            "coder_messages": [response],
        }

    return coder_node


def invoke_with_retry(
    llm,
    messages,
    max_attempts,
):
    for attempt in range(1, max_attempts + 1):
        try:
            return llm.invoke(messages)

        except ResponseValidationError as exc:
            error_text = str(exc)

            transient_provider_error = (
                "ResourceExhausted" in error_text
                or "request limit reached" in error_text
                or '"code":502' in error_text
            )

            if not transient_provider_error:
                raise

            if attempt == max_attempts:
                raise RuntimeError(
                    "The upstream model provider remained unavailable "
                    f"after {max_attempts} attempts."
                ) from exc

            delay_seconds = 2 ** (attempt - 1)
            time.sleep(delay_seconds)
