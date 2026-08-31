from __future__ import annotations

import argparse
import platform

from .chat import ChatSession, ConfigurationError, OpenAIResponsesClient
from .drive import DriveController
from .motion import Motion
from .transport import MemoryTransport


def main() -> None:
    parser = argparse.ArgumentParser(prog="bertrobo")
    parser.add_argument("command", choices=("doctor", "demo", "chat"))
    args = parser.parse_args()

    if args.command == "doctor":
        print(f"Python platform: {platform.platform()}")
        print("Motor transport: not configured (safe default)")
        print("Ready: install serial/GPIO adapters only on the Raspberry Pi.")
        return

    if args.command == "chat":
        run_chat()
        return

    transport = MemoryTransport()
    drive = DriveController(transport)
    drive.command(Motion.FORWARD, 25)
    drive.stop()
    print("Simulation commands:")
    print(b"".join(transport.writes).decode("ascii"), end="")


def run_chat() -> None:
    """Run the Stage 1 text-only companion loop."""
    try:
        session = ChatSession(OpenAIResponsesClient.from_environment())
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        return

    print("BertRobo text chat. Type 'quit' or press Ctrl-C to exit.")
    while True:
        try:
            user_text = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBertRobo: Goodbye.")
            return

        if user_text.lower() in {"quit", "exit"}:
            print("BertRobo: Goodbye.")
            return
        if not user_text:
            continue

        try:
            print(f"BertRobo: {session.reply(user_text)}")
        except RuntimeError as error:
            print(f"BertRobo: I couldn't reach my language service: {error}")


if __name__ == "__main__":
    main()
