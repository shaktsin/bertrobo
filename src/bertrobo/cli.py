from __future__ import annotations

import argparse
import platform

from .drive import DriveController
from .motion import Motion
from .transport import MemoryTransport


def main() -> None:
    parser = argparse.ArgumentParser(prog="bertrobo")
    parser.add_argument("command", choices=("doctor", "demo"))
    args = parser.parse_args()

    if args.command == "doctor":
        print(f"Python platform: {platform.platform()}")
        print("Motor transport: not configured (safe default)")
        print("Ready: install serial/GPIO adapters only on the Raspberry Pi.")
        return

    transport = MemoryTransport()
    drive = DriveController(transport)
    drive.command(Motion.FORWARD, 25)
    drive.stop()
    print("Simulation commands:")
    print(b"".join(transport.writes).decode("ascii"), end="")


if __name__ == "__main__":
    main()
