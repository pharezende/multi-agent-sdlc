import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the multi-agent SDLC workflow.")

    parser.add_argument(
        "--resume",
        metavar="THREAD_ID",
        help="Resume the workflow identified by THREAD_ID.",
    )

    parser.add_argument(
        "--auto-approve-plan",
        action="store_true",
        help="Automatically approve plan reviews.",
    )

    return parser.parse_args()
