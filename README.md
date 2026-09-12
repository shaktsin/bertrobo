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

## Stage 1 text chat

Create an OpenAI API key, then set it only in the Pi shell (never commit it):

```sh
export OPENAI_API_KEY="your_api_key"
export BERTROBO_MODEL="gpt-5-mini" # optional; this is the default
.venv/bin/python -m bertrobo chat
```

Type a message, then use `quit` or Ctrl-C to leave. This chat is text-only and has no access to hardware actions, tools, or persistent memory.

## Stage 2 voice chat

Connect a USB microphone and USB-audio speaker, then install the Pi audio tools and start push-to-talk voice mode:

```sh
sudo apt install -y alsa-utils
export OPENAI_API_KEY="your_api_key"
.venv/bin/python -m bertrobo voice
```

If the Pi's ALSA `default` device is not configured for both microphone input and speaker output, select the USB devices explicitly. For the USB microphone and CA-2110USB speaker currently used by this project:

```sh
export BERTROBO_CAPTURE_DEVICE="plughw:3,0"
export BERTROBO_PLAYBACK_DEVICE="plughw:2,0"
.venv/bin/python -m bertrobo voice
```

Find device numbers with `arecord -l` (microphone) and `aplay -l` (speaker). These values can change if USB devices are unplugged or connected in a different order.

Press Enter, speak for five seconds, and BertRobo will transcribe your voice, answer, and play the answer through the selected USB speaker. The first version uses push-to-talk; automatic voice interruption/echo cancellation is intentionally deferred until the microphone and speaker have been verified together.

For Pi installation and the hardware checklist, see [docs/setup-pi.md](docs/setup-pi.md) and [docs/hardware.md](docs/hardware.md). The project’s canonical [design](docs/design.md), [goals](docs/goals.md), and [10-stage implementation plan](docs/implementation-plan.md) define the build order. The complete source conversation remains in [docs/shared-chat-transcript.md](docs/shared-chat-transcript.md).

## Safety boundary

Do not connect motors directly to a Raspberry Pi. Use a motor driver powered from an appropriate, separately fused motor supply. Keep a physical emergency-stop or master power switch in reach during bring-up.
