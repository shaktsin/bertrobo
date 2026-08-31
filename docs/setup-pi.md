# Raspberry Pi setup and bring-up

Use Raspberry Pi OS 64-bit on the Pi. Keep macOS as the development environment and connect to the Pi over Wi-Fi/Ethernet with SSH.

## 1. Base install

1. Flash current Raspberry Pi OS 64-bit with Raspberry Pi Imager.
2. Set hostname, Wi-Fi, locale, and enable SSH in Imager before first boot.
3. Boot with the active cooler installed; update packages and reboot.
4. From the Mac, verify `ssh <user>@<hostname>.local` and clone this repository.

## 2. Project install

```sh
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y python3-venv python3-pip git
git clone <your-repository-url> bertrobo
cd bertrobo
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m bertrobo doctor
.venv/bin/python -m pytest
```

## Stage 1 LLM chat

In the Pi shell, set the API key for the current session. Do not add it to Git or paste it into source files:

```sh
export OPENAI_API_KEY="your_api_key"
.venv/bin/python -m bertrobo chat
```

Enter `hello` and verify that BertRobo returns a text response. Use `quit` to leave. `BERTROBO_MODEL` optionally selects a different compatible model; it defaults to `gpt-5-mini`.

## 3. Test in this order

1. Run `bertrobo demo` on the Mac or Pi; it is simulation-only.
2. Test the ESP32 firmware with wheels lifted off the bench and motor power disconnected initially.
3. Verify the ESP32 watchdog stops motors when serial commands stop.
4. Integrate a single sensor, then camera/audio, before autonomous behaviors.
5. Perform the first floor test at low speed with an operator and physical power cutoff present.

## ESP32 serial protocol

The Python starter sends ASCII lines such as:

```text
DRIVE forward 25
DRIVE left 30
DRIVE stop 0
```

Firmware should reject malformed input, cap speed, and force STOP after a short command timeout. This protocol is intentionally simple so it can be inspected with a serial monitor during bring-up.
