import math
import random
import time
from datetime import datetime, timezone

import requests


# ============================================================
# VAYUNEXA AI FLAP CONTROL SIMULATOR
# ============================================================

API_BASE = "http://127.0.0.1:8000/api/v1"

TELEMETRY_URL = f"{API_BASE}/telemetry"
AUTO_CONTROL_URL = f"{API_BASE}/control/auto"

API_KEY = "dev-token-change-me"
DEVICE_ID = "VAYU-001"

INTERVAL_SECONDS = 5

MIN_FLAP_ANGLE = 5.0
MAX_FLAP_ANGLE = 35.0


# ============================================================
# HELPERS
# ============================================================

def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


# ============================================================
# SIMULATED ENVIRONMENT
# ============================================================

def generate_environment(step):
    """
    Generate changing wind/weather conditions.

    This represents sensors + weather data that would
    eventually come from the real ESP8266 and weather API.
    """

    wind = (
        8.0
        + math.sin(step * 0.35) * 1.8
        + math.sin(step * 0.11) * 0.8
        + random.uniform(-0.25, 0.25)
    )

    wind = clamp(wind, 3.0, 14.0)

    direction = (
        220
        + math.sin(step * 0.18) * 25
        + random.uniform(-3, 3)
    ) % 360

    temperature = (
        29.5
        + math.sin(step * 0.08) * 2.0
        + random.uniform(-0.2, 0.2)
    )

    humidity = (
        76
        + math.sin(step * 0.12) * 5
        + random.uniform(-1, 1)
    )

    # Simulated weather conditions
    precipitation = max(
        0.0,
        math.sin(step * 0.07) * 1.5
        + random.uniform(-0.2, 0.2),
    )

    cloud_cover = clamp(
        65
        + math.sin(step * 0.05) * 25
        + random.uniform(-5, 5),
        0,
        100,
    )

    return {
        "wind": wind,
        "direction": direction,
        "temperature": temperature,
        "humidity": clamp(humidity, 45, 95),
        "precipitation": precipitation,
        "cloud_cover": cloud_cover,
    }


# ============================================================
# POWER MODEL
# ============================================================

def calculate_power(
    wind,
    flap_1,
    flap_2,
    flap_3,
):
    """
    Prototype aerodynamic response model.

    IMPORTANT:
    This is NOT a real turbine aerodynamic model.
    It exists only for simulation/demo purposes.
    """

    average_flap = (
        flap_1
        + flap_2
        + flap_3
    ) / 3.0

    aerodynamic_factor = (
        1
        + (average_flap - 15) * 0.012
    )

    power = (
        0.12
        * wind ** 3
        * aerodynamic_factor
    )

    return clamp(power, 20, 180)


# ============================================================
# SEND TELEMETRY
# ============================================================

def send_telemetry(
    environment,
    rpm,
    power,
    flap_1,
    flap_2,
    flap_3,
    servo_energy,
):
    voltage = 24.0

    current = power / voltage

    payload = {
        "device_id": DEVICE_ID,

        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),

        "wind_speed": round(
            environment["wind"],
            2,
        ),

        "wind_direction": round(
            environment["direction"],
            1,
        ),

        "rpm": round(
            rpm,
            1,
        ),

        "voltage": round(
            voltage,
            2,
        ),

        "current": round(
            current,
            3,
        ),

        "power": round(
            power,
            2,
        ),

        "flap_angle_1": round(
            flap_1,
            1,
        ),

        "flap_angle_2": round(
            flap_2,
            1,
        ),

        "flap_angle_3": round(
            flap_3,
            1,
        ),

        "temperature": round(
            environment["temperature"],
            1,
        ),

        "humidity": round(
            environment["humidity"],
            1,
        ),

        "mode": "simulation",

        "servo_energy_wh": round(
            servo_energy,
            6,
        ),
    }

    response = requests.post(
        TELEMETRY_URL,
        json=payload,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        timeout=5,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# ASK AUTO CONTROLLER
# ============================================================

def get_auto_target():
    """
    Ask backend for the optimal flap configuration.
    """

    body = {
        "device_id": DEVICE_ID,
    }

    response = requests.post(
        AUTO_CONTROL_URL,
        json=body,
        headers={
            "x-api-key": API_KEY,
            "Content-Type": "application/json",
        },
        timeout=5,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# MAIN CONTROL LOOP
# ============================================================

def main():

    print("=" * 75)
    print("VAYUNEXA AI FLAP CONTROL SIMULATOR")
    print("=" * 75)

    print(f"Device:       {DEVICE_ID}")
    print(f"Backend:      {API_BASE}")
    print(f"Interval:     {INTERVAL_SECONDS}s")
    print("Control:      AI / AUTO")
    print("Flap range:   5 - 35 degrees")
    print("Environment:  WIND + WEATHER")
    print("Press CTRL+C to stop.")

    print("=" * 75)

    step = 0

    # Current physical flap positions
    flap_1 = 18.0
    flap_2 = 18.0
    flap_3 = 18.0

    while True:

        try:

            # ==================================================
            # STEP 1
            # Generate NEW environment
            # ==================================================

            environment = generate_environment(step)

            wind = environment["wind"]

            direction = environment["direction"]

            temperature = environment["temperature"]

            humidity = environment["humidity"]

            precipitation = environment["precipitation"]

            cloud_cover = environment["cloud_cover"]


            # ==================================================
            # STEP 2
            # Estimate current rotor response
            # ==================================================

            rpm = 350 + wind * 68

            current_power = calculate_power(
                wind,
                flap_1,
                flap_2,
                flap_3,
            )


            # ==================================================
            # STEP 3
            # SEND CURRENT TELEMETRY
            # ==================================================

            telemetry_result = send_telemetry(
                environment=environment,
                rpm=rpm,
                power=current_power,
                flap_1=flap_1,
                flap_2=flap_2,
                flap_3=flap_3,
                servo_energy=0.0,
            )


            # ==================================================
            # STEP 4
            # ASK AI CONTROLLER
            # ==================================================

            decision = get_auto_target()

            target_angles = decision.get(
                "target_angles",
                {},
            )

            target_1 = float(
                target_angles.get(
                    "flap_1",
                    flap_1,
                )
            )

            target_2 = float(
                target_angles.get(
                    "flap_2",
                    flap_2,
                )
            )

            target_3 = float(
                target_angles.get(
                    "flap_3",
                    flap_3,
                )
            )


            # ==================================================
            # STEP 5
            # SAFETY CLAMP
            # ==================================================

            target_1 = clamp(
                target_1,
                MIN_FLAP_ANGLE,
                MAX_FLAP_ANGLE,
            )

            target_2 = clamp(
                target_2,
                MIN_FLAP_ANGLE,
                MAX_FLAP_ANGLE,
            )

            target_3 = clamp(
                target_3,
                MIN_FLAP_ANGLE,
                MAX_FLAP_ANGLE,
            )


            # ==================================================
            # STEP 6
            # SIMULATE SERVO MOVEMENT
            # ==================================================

            previous_angles = (
                flap_1,
                flap_2,
                flap_3,
            )

            flap_1 = target_1
            flap_2 = target_2
            flap_3 = target_3

            movement = (
                abs(flap_1 - previous_angles[0])
                + abs(flap_2 - previous_angles[1])
                + abs(flap_3 - previous_angles[2])
            )

            servo_energy = (
                movement * 0.0005
            )


            # ==================================================
            # STEP 7
            # CALCULATE NEW POWER AFTER AI MOVEMENT
            # ==================================================

            optimized_power = calculate_power(
                wind,
                flap_1,
                flap_2,
                flap_3,
            )


            # ==================================================
            # STEP 8
            # DISPLAY COMPLETE AI DECISION
            # ==================================================

            safety_status = decision.get(
                "safety_status",
                "SAFE",
            )

            reason = decision.get(
                "reason",
                "AI optimization",
            )

            gain = decision.get(
                "expected_power_gain_percent",
                0.0,
            )

            print(
                f"[{step:04d}] "
                f"WIND={wind:5.2f} m/s | "
                f"POWER={optimized_power:6.2f} W | "
                f"AI="
                f"{target_1:4.1f}/"
                f"{target_2:4.1f}/"
                f"{target_3:4.1f}° | "
                f"FLAPS="
                f"{flap_1:4.1f}/"
                f"{flap_2:4.1f}/"
                f"{flap_3:4.1f}° | "
                f"SAFE={safety_status} | "
                f"GAIN={gain}%"
            )

            print(
                f"       WEATHER: "
                f"TEMP={temperature:4.1f}°C | "
                f"HUM={humidity:4.1f}% | "
                f"RAIN={precipitation:4.2f} | "
                f"CLOUD={cloud_cover:5.1f}%"
            )

            print(
                f"       AI REASON: {reason}"
            )

            print(
                f"       API: "
                f"{telemetry_result.get('status', 'OK')}"
            )

            print("-" * 75)


            step += 1

            time.sleep(
                INTERVAL_SECONDS
            )


        except KeyboardInterrupt:

            print(
                "\nAI simulator stopped."
            )

            break


        except requests.RequestException as error:

            print(
                f"[API ERROR] {error}"
            )

            print(
                "Retrying in 5 seconds..."
            )

            time.sleep(5)


        except Exception as error:

            print(
                f"[ERROR] "
                f"{type(error).__name__}: "
                f"{error}"
            )

            time.sleep(5)


if __name__ == "__main__":
    main()