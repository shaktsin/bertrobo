from __future__ import annotations

from .motion import DriveCommand, Motion
from .transport import ByteTransport


class DriveController:
    """High-level drive interface; the ESP32 remains the motor authority."""

    def __init__(self, transport: ByteTransport) -> None:
        self._transport = transport
        self.last_command = DriveCommand(Motion.STOP)

    def command(self, motion: Motion, speed: int = 0) -> DriveCommand:
        command = DriveCommand(motion, speed)
        self._transport.write(command.encode())
        self.last_command = command
        return command

    def stop(self) -> DriveCommand:
        return self.command(Motion.STOP)

    def close(self) -> None:
        # Always try to stop before releasing the link.
        try:
            self.stop()
        finally:
            self._transport.close()
