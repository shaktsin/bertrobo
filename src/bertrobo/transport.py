from __future__ import annotations

from typing import Protocol


class ByteTransport(Protocol):
    def write(self, data: bytes) -> int: ...

    def close(self) -> None: ...


class MemoryTransport:
    """A harmless transport for development and automated tests."""

    def __init__(self) -> None:
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> int:
        if self.closed:
            raise RuntimeError("transport is closed")
        self.writes.append(data)
        return len(data)

    def close(self) -> None:
        self.closed = True
