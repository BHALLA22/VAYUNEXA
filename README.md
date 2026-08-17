# VAYUNEXA

### AI-Powered Adaptive Wind Energy Optimization & Predictive Control System

VAYUNEXA is an intelligent wind-energy optimization platform that combines **IoT hardware, adaptive aerodynamic flap control, real-time telemetry, weather intelligence, and AI-based energy prediction** to improve the efficiency and stability of small-scale wind turbines.

The system continuously monitors wind and turbine conditions, predicts energy generation, determines optimal flap positions, and communicates control commands to an ESP8266-based hardware controller.

---

## Project Overview

Traditional small-scale wind turbines generally operate with fixed blade geometry. Their efficiency can decrease significantly when wind conditions change.

VAYUNEXA introduces an **adaptive flap mechanism** into the turbine blade design.

Each turbine blade contains a movable flap section controlled by a servo motor.

The system can:

- Monitor wind speed in real time
- Monitor turbine electrical parameters
- Predict future energy generation
- Analyze weather conditions
- Calculate optimized flap angles
- Send control commands to ESP8266
- Move individual blade flaps using servo motors
- Compare adaptive operation against fixed-blade operation
- Display real-time system information through a web dashboard

The goal is to maximize useful energy generation while maintaining safe turbine operation.

---

# Key Features

## 1. Adaptive Flap Control

The turbine contains three independently controlled aerodynamic flaps.

Each flap can be positioned according to current operating conditions.

Example:

```text
Blade 1 → 18°
Blade 2 → 21°
Blade 3 → 19°
