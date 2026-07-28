from multi_agent_sdlc.state import DevState
from .graph import build_graph


def run() -> None:
    graph = build_graph()

    initial_state: DevState = {
        "request": "Build a calculator app, all end user interactions happens via the terminal.",
        "plan": None,
        "project_directory": "",
        "coder_messages": [],
    }

    result = graph.invoke(initial_state)

    print("\nDone!")


if __name__ == "__main__":
    run()
