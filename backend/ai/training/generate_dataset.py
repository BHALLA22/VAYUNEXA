import math
import random
from pathlib import Path

import pandas as pd


# ============================================================
# VAYUNEXA AI - PROTOTYPE DATASET GENERATOR
# ============================================================

OUTPUT_PATH = Path(
    "ai/data/training_dataset.csv"
)

RANDOM_SEED = 42

random.seed(RANDOM_SEED)


# ============================================================
# CONFIGURATION
# ============================================================

SAMPLES = 10000

MIN_FLAP = 5.0
MAX_FLAP = 35.0


# ============================================================
# POWER SIMULATION
# ============================================================

def calculate_power(
    wind_speed,
    wind_direction,
    rpm,
    temperature,
    humidity,
    flap_angle,
):
    """
    Physics-inspired prototype power model.

    This is synthetic training data.

    It must NOT be treated as measured turbine data.
    """

    # --------------------------------------------------------
    # Base wind power relationship
    # --------------------------------------------------------

    wind_component = (
        0.12 * wind_speed ** 3
    )

    # --------------------------------------------------------
    # Optimal flap angle changes with wind
    # --------------------------------------------------------

    optimal_angle = (
        8
        + wind_speed * 1.8
    )

    optimal_angle = max(
        MIN_FLAP,
        min(MAX_FLAP, optimal_angle),
    )

    # --------------------------------------------------------
    # Penalty for being away from optimal angle
    # --------------------------------------------------------

    angle_error = (
        flap_angle - optimal_angle
    )

    angle_factor = math.exp(
        -(angle_error ** 2) / 120
    )

    # --------------------------------------------------------
    # Wind direction effect
    # --------------------------------------------------------

    direction_factor = (
        0.90
        + 0.10 * abs(
            math.cos(
                math.radians(
                    wind_direction
                )
            )
        )
    )

    # --------------------------------------------------------
    # RPM operating factor
    # --------------------------------------------------------

    expected_rpm = (
        350
        + wind_speed * 68
    )

    rpm_error = (
        rpm - expected_rpm
    )

    rpm_factor = math.exp(
        -(rpm_error ** 2) / 50000
    )

    # --------------------------------------------------------
    # Temperature effect
    # --------------------------------------------------------

    temperature_factor = (
        1
        - abs(
            temperature - 25
        ) * 0.003
    )

    # --------------------------------------------------------
    # Humidity effect
    # --------------------------------------------------------

    humidity_factor = (
        1
        - max(
            0,
            humidity - 80
        ) * 0.001
    )

    # --------------------------------------------------------
    # Combined power
    # --------------------------------------------------------

    power = (
        wind_component
        * angle_factor
        * direction_factor
        * rpm_factor
        * temperature_factor
        * humidity_factor
    )

    # Add realistic measurement noise
    noise = random.gauss(
        0,
        max(0.5, power * 0.02),
    )

    power += noise

    return max(
        0,
        power,
    )


# ============================================================
# DATASET GENERATION
# ============================================================

def generate_dataset():

    rows = []

    for _ in range(SAMPLES):

        # ----------------------------------------------------
        # Environment
        # ----------------------------------------------------

        wind_speed = random.uniform(
            3,
            14,
        )

        wind_direction = random.uniform(
            0,
            360,
        )

        temperature = random.uniform(
            15,
            40,
        )

        humidity = random.uniform(
            40,
            95,
        )

        # ----------------------------------------------------
        # Rotor state
        # ----------------------------------------------------

        rpm = (
            350
            + wind_speed * 68
            + random.gauss(0, 25)
        )

        rpm = max(
            0,
            rpm,
        )

        # ----------------------------------------------------
        # Candidate flap angle
        # ----------------------------------------------------

        flap_angle = random.uniform(
            MIN_FLAP,
            MAX_FLAP,
        )

        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        power = calculate_power(
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            rpm=rpm,
            temperature=temperature,
            humidity=humidity,
            flap_angle=flap_angle,
        )

        rows.append(
            {
                "wind_speed": round(
                    wind_speed,
                    3,
                ),
                "wind_direction": round(
                    wind_direction,
                    2,
                ),
                "rpm": round(
                    rpm,
                    2,
                ),
                "temperature": round(
                    temperature,
                    2,
                ),
                "humidity": round(
                    humidity,
                    2,
                ),
                "flap_angle": round(
                    flap_angle,
                    2,
                ),
                "power": round(
                    power,
                    3,
                ),
            }
        )

    dataframe = pd.DataFrame(
        rows
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print("=" * 60)
    print("VAYUNEXA TRAINING DATASET")
    print("=" * 60)

    print(
        f"Samples: {len(dataframe)}"
    )

    print(
        f"Output:  {OUTPUT_PATH}"
    )

    print()

    print(
        dataframe.head(10)
    )

    print()

    print(
        "Dataset statistics:"
    )

    print(
        dataframe.describe()
    )


if __name__ == "__main__":
    generate_dataset()