# Detailed robot build plan

This turns the shared chat into an executable plan. Complete each exit check before buying or integrating the next stage. Prices and local-stock claims in the transcript are snapshots only; use current listings when purchasing.

## Stage 0 — Safety and project setup

1. Read the [hardware plan](hardware.md) and select the target chassis size, motor voltage, and battery chemistry.
2. Keep a multimeter, eye protection, a fuse holder, and a reachable master power switch in the build area.
3. Create a wiring diagram before connecting a battery. Record the motor’s stall current and choose a driver and fuse rated above it.
4. Never power motors from the Pi. The Pi is the high-level brain; the ESP32 and motor driver are the motion boundary.

**Exit check:** a written power/wiring diagram identifies every supply rail, common ground point, fuse, switch, and connector.

## Stage 1 — Pi brain on the desk

Buy only: Raspberry Pi 5 (the shared chat settles on 4 GB for the initial POC), official 27 W USB-C supply, active cooler, and 64 GB+ microSD card.

1. Flash current Raspberry Pi OS 64-bit using Raspberry Pi Imager.
2. In Imager, configure a hostname, Wi-Fi, locale, user account, and SSH access.
3. Install the active cooler, boot the Pi, and update it: `sudo apt update && sudo apt full-upgrade -y`.
4. From the Mac, SSH to the Pi and clone this repository.
5. Create the virtual environment and run `python3 -m bertrobo doctor`.
6. Confirm network connectivity and a clean reboot.

**Exit check:** the Pi can be reached by SSH from the Mac after reboot and runs the project’s `doctor` command.

## Stage 2 — Software skeleton and remote workflow

1. Develop on macOS with Git and VS Code; run hardware-facing code on the Pi through SSH.
2. Run `python3 -m bertrobo demo`; it must only emit simulated serial commands.
3. Run tests with `python3 -m pytest`.
4. Add configuration for host name, serial port, camera, and sensors only after each device is physically verified.
5. Keep cloud-model credentials in environment variables or a local untracked `.env` file, never in Git.

**Exit check:** all tests pass and the code operates without hardware connected.

## Stage 3 — Motion base and ESP32

Buy: chassis, geared motors (prefer encoders), wheels/caster, ESP32 dev board, motor driver matched to motor stall current, motor battery, buck converter, fuse, switch, wire, connectors, and mounting hardware.

1. Assemble the chassis mechanically with the battery disconnected.
2. Wire the ESP32 to the motor driver; keep the Pi out of the motor-power path.
3. Implement ESP32 firmware that accepts only valid `DRIVE <direction> <speed>` commands, caps PWM, and stops on malformed input.
4. Add a short command watchdog in ESP32 firmware that returns both motors to STOP when commands stop arriving.
5. Connect Pi ↔ ESP32 by USB serial and validate the `DRIVE` protocol with the wheels off the floor.
6. Test forward, reverse, left, right, stop, USB disconnect, Pi process crash, and master switch.

**Exit check:** every failure case stops the motors, including unplugging the Pi or terminating the Pi process.

## Stage 4 — Sensors and perception

Buy/integrate one at a time: ToF distance sensor, bumper switches, camera module, then microphone/speaker.

1. Enable I²C and scan for the first distance sensor; confirm its measured range while stationary.
2. Add bumper switches as a hardware-adjacent stop condition.
3. Attach and validate the Pi Camera Module with a simple local capture test.
4. Add microphone input and speaker output, then test an offline record/playback loop.
5. Expose each device through a small adapter module and test it independently before joining it to behavior logic.

**Exit check:** each sensor/camera/audio component has a standalone smoke test and a documented connector/pin assignment.

## Stage 5 — Behaviors and agent layer

1. Start with deterministic behaviors: manual low-speed driving, obstacle stop, turn toward a detected target, and scripted speech.
2. Build the high-level control loop so perception suggests actions; a safety layer validates every action before it reaches the drive controller.
3. If using an LLM, limit it to intents such as `greet`, `look_at`, or `move_forward` with explicit arguments. Do not give it unrestricted raw motor access.
4. Add telemetry: last drive command, battery voltage, sensor distances, command timeouts, and errors.
5. Only introduce autonomous movement after repeatable supervised tests on a clear floor.

**Exit check:** the robot demonstrates a supervised scripted interaction and stops safely whenever its sensor or command link fails.

## First-day commands

Run these from the project root after cloning on a Pi:

```sh
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-pip git
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m bertrobo doctor
.venv/bin/python -m bertrobo demo
.venv/bin/python -m pytest
```

The starter protocol is intentionally inspectable:

```text
DRIVE forward 25
DRIVE left 30
DRIVE stop 0
```

The ESP32 must treat `stop` and any timeout as authoritative and must not resume motion without a fresh valid command.
