# BertRobo goals and milestones

## North-star goal

Build a cute autonomous AI companion that can **see → hear → understand → remember → reason → express → move → act** while keeping the hardware modular and the differentiation in software.

## Current goal — Stage 1: Brain

Run a reliable agent on Raspberry Pi 5 that is developed from a Mac through SSH and can respond to typed input using an LLM.

**Done when:** from the Mac, a user sends `hello` to a program running on the Pi and receives an LLM-backed response.

## Stage goals

| Stage | Goal | Done when |
| --- | --- | --- |
| 1. Brain | Pi, SSH, Python, project, LLM | Typed conversation works from the Mac. |
| 2. Hear + speak | Voice conversation | The robot answers spoken requests and reliably handles interruptions. |
| 3. Vision | Person/object/scene perception | It identifies a person, location, and basic objects. |
| 4. Memory | Persistent user and world memory | Facts survive restarts and can be recalled later. |
| 5. Character | Face, emotions, head tracking | It looks toward people and expresses behavior state. |
| 6. Mobile body | Safe commanded movement | It moves, turns, and stops reliably under ESP32 control. |
| 7. Spatial awareness | Collision prevention | It stops for obstacles and can request help or reroute. |
| 8. Autonomous behaviors | Goal-directed multi-step actions | It combines perception, memory, and actions sensibly. |
| 9. Navigation | Room-to-room autonomy | It localizes and navigates named locations. |
| 10. Product prototype | Productizable embodiment | The validated experience moves to enclosure, PCB, power management, and manufacturable design. |

## Demonstrations that matter

1. **Brain:** Pi talks to an LLM.
2. **Companion:** it sees, hears, talks, and remembers.
3. **Character:** it has a face, expressions, personality, and attention.
4. **Robot:** it moves, follows, and avoids obstacles.
5. **Autonomous companion:** it observes, remembers, and proactively performs useful behaviors.

## Non-goals for the first prototype

- Custom PCBs, a custom enclosure, LiDAR, SLAM/ROS2, robotic arms, and a charging dock.
- Optimizing mobility before the companion interaction is compelling.
- Letting an LLM produce raw GPIO, servo-PWM, or motor-driver commands.
