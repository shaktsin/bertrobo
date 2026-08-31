# 10-stage implementation plan

The stages below are the authoritative build order. Advance only after the listed demonstration works reliably.

## 1. Brain

Install Raspberry Pi OS 64-bit, Wi-Fi, SSH, Python, Git, and this project. Develop from macOS with SSH. Add an LLM client and text chat loop.

**Demonstrate:** typed `hello` from the Mac receives a response from the application running on the Pi.

## 2. Hearing and speech

Add a USB microphone and powered speaker. Build speech-to-text → agent → text-to-speech and make speech interruption cancel playback before listening again.

**Demonstrate:** ask a spoken question and hear the answer; interrupt it mid-answer and receive a fresh response.

## 3. Vision

Connect Camera Module 3, validate capture, then add person, face, and basic object detection. Keep this desk-mounted and independent of movement.

**Demonstrate:** report person presence/location and answer a basic visual question about a held object.

## 4. Memory

Implement short-term conversation context, persistent user facts, events, and a structured world state (`people`, `objects`, `rooms`, `events`, `relationships`). Retrieve memories by relevance and recency.

**Demonstrate:** store a fact, restart the program, and correctly recall it later.

## 5. Personality and face

Add a 5-inch display, ESP32-S3, two micro servos, and pan/tilt mount. Map behavior states—not LLM animation frames—to face animations, sound, and head movement.

**Demonstrate:** the robot tracks a person laterally, shows thinking while processing, and changes expression while responding.

## 6. Mobile body

Add chassis, encoder motors, wheels, caster, motor driver, battery, buck converter, fuse, and master switch. Pi communicates by USB serial. ESP32 validates commands, controls PWM/encoders, and stops on timeout. Test with wheels lifted before a supervised floor test.

**Demonstrate:** reliable forward motion, turn, and stop from approved high-level commands; unplugging the Pi stops motors.

## 7. Spatial awareness

Add three ToF sensors, IMU, and bumper switches. Introduce a safety controller between requested movement and the ESP32 command channel.

**Demonstrate:** an obstacle or bumper prevents a requested movement from continuing.

## 8. Autonomous behaviors

Combine world state from vision, speech, memory, and sensors with a goal planner and behavior engine. Actions remain semantic: talk, look, move, wait, or ask for help.

**Demonstrate:** recognize an arriving known person, retrieve context, look toward them, express an appropriate emotion, and greet them without scripting each low-level action.

## 9. Navigation

Only after safety and behavior work, evaluate LiDAR/depth, SLAM, ROS2, maps, and a charging dock.

**Demonstrate:** autonomous room-to-room navigation to a named location.

## 10. Product prototype

Replace breadboards and generic chassis with a custom enclosure, integrated power management, consolidated electronics/PCB, and manufacturing-oriented design.

**Demonstrate:** a repeatable, maintainable prototype that preserves the proven companion experience.

## Core prototype budget

The intended core POC is approximately $400–500: brain (~$145), hearing/speech (~$40), vision (~$35), face/head (~$75), movement (~$125), and spatial sensing (~$50). Treat these as planning ranges, not current prices.
