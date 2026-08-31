from bertrobo.drive import DriveController
from bertrobo.motion import Motion
from bertrobo.transport import MemoryTransport


def test_drive_encodes_and_stops() -> None:
    transport = MemoryTransport()
    drive = DriveController(transport)

    drive.command(Motion.LEFT, 30)
    drive.stop()

    assert transport.writes == [b"DRIVE left 30\n", b"DRIVE stop 0\n"]


def test_close_stops_before_closing() -> None:
    transport = MemoryTransport()
    drive = DriveController(transport)

    drive.close()

    assert transport.writes == [b"DRIVE stop 0\n"]
    assert transport.closed
