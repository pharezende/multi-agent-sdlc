import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-agent SDLC workflow.")

    parser.add_argument(
        "--resume",
        metavar="THREAD_ID",
        help="Resume the workflow identified by THREAD_ID.",
    )

    return parser.parse_args()
