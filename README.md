# BertRobo

A safe, incremental starter project for a Raspberry Pi 5 robot. Develop on a Mac, run on Raspberry Pi OS 64-bit, and keep motor control on an ESP32.

## Architecture

```text
Mac (development) ── SSH/Git ──> Raspberry Pi 5
                                      ├─ camera, microphone, speakers
                                      ├─ sensors over I²C/GPIO
                                      └─ USB serial ──> ESP32 ──> motor driver ──> motors
```

The Pi makes high-level decisions. The ESP32 owns the time-sensitive motor loop and stops motors if commands cease.

## Quick start

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m bertrobo doctor
.venv/bin/python -m bertrobo demo
```

`demo` is deliberately simulation-only. It never opens a serial port or drives GPIO.

For Pi installation and the hardware checklist, see [docs/setup-pi.md](docs/setup-pi.md) and [docs/hardware.md](docs/hardware.md). The complete source conversation and the execution sequence are in [docs/shared-chat-transcript.md](docs/shared-chat-transcript.md) and [docs/implementation-plan.md](docs/implementation-plan.md).

## Safety boundary

Do not connect motors directly to a Raspberry Pi. Use a motor driver powered from an appropriate, separately fused motor supply. Keep a physical emergency-stop or master power switch in reach during bring-up.
