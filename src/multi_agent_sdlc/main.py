from langgraph.graph.state import CompiledStateGraph

from multi_agent_sdlc.models import CoderStatus, TesterStatus
from multi_agent_sdlc.state import DevState

from .graph import build_graph


def generate_diagram(graph: CompiledStateGraph) -> None:

    png_data = graph.get_graph().draw_mermaid_png()

    with open("multi_agent_sdlc_workflow.png", "wb") as file:
        file.write(png_data)


def run() -> None:
    graph = build_graph()

    initial_state: DevState = {
        "request": "Build a CLI expense tracker that lets users add expenses, list them, filter by category or date, and display total spending. Store data locally in a JSON file, validate invalid inputs, and provide clear exit codes and error messages. Include a concise README and a uv-managed Python project with a declared command-line entry point.",
        # "request": "Build an app that sum two numbers. The end user interactions happen via the terminal.",
        # "request": "Build a calculator app, all end user interactions happens via the terminal.",
        # "request": "Build an app that enable the user to compute the area of squares and triangles. The end user interactions happen via the terminal.",
        # "request": "Build a Python command-line application named `temperature-converter`. The application must convert temperatures between Celsius and Fahrenheit.",
        # "request": "Build a Python CLI app named password-strength-checker that accepts a password as an argument and reports weak, medium, or strong using only the standard library.",
        "plan": None,
        "project_directory": None,
        "coder_messages": [],
        "coder_status": CoderStatus.IDLE,
        "current_coder_summary": None,
        "coder_summary_history": [],
        "tester_messages": [],
        "tester_status": TesterStatus.IDLE,
        "current_tester_summary": None,
        "verification_history": [],
        "current_project_verification_result": None,
    }

    result = graph.invoke(
        initial_state,
        config={"run_name": "multi_agent_sdlc"},
    )
    # generate_diagram(graph)
    print("\nDone!")


if __name__ == "__main__":
    run()
