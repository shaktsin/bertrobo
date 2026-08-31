# BertRobo design

## Product vision

BertRobo is a small autonomous AI companion that can **see, hear, understand, remember, reason, express, move, and act**. The first product question is whether a stationary companion that sees, converses, remembers, and expresses personality is compelling. Mobility expands that experience; it does not substitute for it.

## System architecture

```text
                 Optional cloud services
       LLM / VLM / search / durable memory services
                         │
                         ▼
┌────────────────────────────────────────────────────┐
│                    Raspberry Pi 5                   │
│  Vision · Speech · Agent · Memory · World state     │
│               Behavior engine / policies            │
│                 high-level actions                  │
└─────────────────────────┬──────────────────────────┘
                          │ USB serial
                          ▼
                  ┌──────────────┐
                  │    ESP32     │
                  │ real-time IO │
                  └───┬────┬─────┘
                      │    │
           motors/encoders servos/sensors/LEDs
```

The Pi owns perception, memory, planning, personality, and high-level behavior. The ESP32 owns latency-sensitive physical control: PWM, encoder feedback, motor stopping, and simple local safety. Cloud AI is optional and initially supplies compute-intensive capabilities.

## Design rules

1. Hardware is replaceable; agent and behavior code must use semantic actions such as `look_at(person)` and `move(distance)` rather than pin numbers or PWM values.
2. AI cannot directly control motors. All physical actions pass through a policy/safety layer; the ESP32 watchdog stops the robot on lost commands.
3. Develop on macOS and run robot services on Raspberry Pi OS 64-bit over SSH.
4. Integrate and demonstrate one subsystem at a time. Do not buy navigation hardware or build custom electronics before the companion experience works.
5. A physical master switch, motor fuse, isolated motor power rail, and supervised bench tests are required before any floor test.

## Software boundaries

```text
brain/        agent, LLM client, planner
perception/   vision, speech-to-text, audio input
memory/       short-term, user, event, world model
behavior/     emotions, policies, action selection
hardware/     ESP32 transport, motors, servos, sensors
interface/    display face, text and voice output
```

The behavior engine converts intent and world state into approved actions. Hardware adapters translate approved actions to device-specific protocols. This lets a later production chassis replace the prototype without rewriting the intelligence layer.

## Safety contract

- Pi sends bounded high-level commands; ESP32 validates them and independently enforces a command timeout.
- A safety controller can veto movement when distance, bumper, battery, or communication state is unsafe.
- Motors never receive power from Pi GPIO or the Pi 5 V rail.
- Unknown component voltage/current limits are verified from their datasheets before wiring.
