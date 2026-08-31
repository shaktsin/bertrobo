# Hardware plan and bill of materials

This is the staged v0 hardware plan distilled from the shared design conversation. Buy and validate a stage before expanding it.

| Stage | Parts | Purpose |
| --- | --- | --- |
| Compute | Raspberry Pi 5 (8 GB recommended), official 27 W USB-C PSU, active cooler, microSD (64 GB+ high endurance) | Main robot computer |
| Chassis | 2WD/4WD chassis, geared DC motors, wheels, caster, fasteners | Mobile base |
| Motor control | ESP32 dev board, dual H-bridge driver sized for the motors (TB6612FNG for small motors; higher-current driver otherwise), fuse, motor battery and buck converter | Isolated, real-time motor control |
| Vision | Raspberry Pi Camera Module 3 (wide if needed), ribbon cable | Vision |
| Audio | USB microphone or ReSpeaker-class audio board; small amplified speaker | Voice I/O |
| Distance/safety | VL53L0X/VL53L1X ToF sensor, bumper switches, physical E-stop/master switch | Obstacle and human safety |
| Wiring | JST/Dupont leads, terminal blocks, heat-shrink, wire ferrules, multimeter | Reliable assembly |

## Power rules

- Power the Pi from its official USB-C supply or a regulated 5 V rail with enough current headroom.
- Power motors from their own battery/rail through the driver; share ground with the ESP32/Pi only where the design calls for it.
- Fuse the motor supply near the battery and add a reachable master switch.
- Do not use the Pi’s 5 V rail to power motors, and never drive motors from GPIO.

## Pin and link plan

- Pi ↔ ESP32: USB serial first; use UART only after stable bench testing.
- Pi ↔ sensors: I²C, with each sensor’s voltage level verified first.
- Pi ↔ Camera Module 3: CSI ribbon connector.
- ESP32 ↔ motor driver: GPIO direction/PWM lines; the ESP32 firmware must time out to STOP if it stops receiving commands.

Record actual pins, battery chemistry, motor stall current, and driver model in a wiring diagram before applying power.
