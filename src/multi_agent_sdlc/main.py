from multi_agent_sdlc.state import DevState
from .graph import build_graph


def run() -> None:
    graph = build_graph()

    initial_state: DevState = {
        "request": "Build a calculator app, all end user interactions happens via the terminal.",
        # "request": "Build an app that enable the user to compute the area of squares and triangles. The end user interactions happen via the terminal.",
        # "request": "Build a Python command-line application named `temperature-converter`. The application must convert temperatures between Celsius and Fahrenheit.",
        # "request": "Build a Python CLI app named password-strength-checker that accepts a password as an argument and reports weak, medium, or strong using only the standard library.",
        "plan": None,
        "project_directory": "",
        "coder_messages": [],
    }

    result = graph.invoke(initial_state)

    print("\nDone!")


if __name__ == "__main__":
    run()
