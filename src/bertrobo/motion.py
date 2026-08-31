from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Motion(str, Enum):
    STOP = "stop"
    FORWARD = "forward"
    REVERSE = "reverse"
    LEFT = "left"
    RIGHT = "right"


@dataclass(frozen=True)
class DriveCommand:
    motion: Motion
    speed: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.speed <= 100:
            raise ValueError("speed must be between 0 and 100")
        if self.motion is Motion.STOP and self.speed != 0:
            raise ValueError("stop commands must use speed 0")
        if self.motion is not Motion.STOP and self.speed == 0:
            raise ValueError("moving commands must have a non-zero speed")

    def encode(self) -> bytes:
        """Stable newline-delimited protocol sent to the ESP32."""
        return f"DRIVE {self.motion.value} {self.speed}\n".encode("ascii")
