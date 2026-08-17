"""
VAYUNEXA AI POWER PREDICTION SERVICE

Trained model:
    RandomForestRegressor

Model version:
    vayu-rf-v1

Training features:
    wind_speed
    wind_direction
    rpm
    temperature
    humidity
    flap_angle

Target:
    power

IMPORTANT:
The trained model uses ONE flap_angle value.
For the physical 3-flap turbine, we represent this
as the average of flap_angle_1, flap_angle_2 and
flap_angle_3.
"""

from pathlib import Path

import joblib
import pandas as pd


# =========================================================
# MODEL PATH
# =========================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    BACKEND_DIR
    / "ai"
    / "models"
    / "power_predictor.joblib"
)


# =========================================================
# MODEL CACHE
# =========================================================

_model_package = None


def get_model_package():
    """
    Load the trained model package once.
    """

    global _model_package

    if _model_package is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"AI model not found: {MODEL_PATH}"
            )

        _model_package = joblib.load(
            MODEL_PATH
        )

        if not isinstance(
            _model_package,
            dict,
        ):
            raise ValueError(
                "Invalid AI model package."
            )

        required_keys = {
            "model",
            "features",
            "target",
            "model_version",
        }

        missing = (
            required_keys
            - set(_model_package.keys())
        )

        if missing:
            raise ValueError(
                "Model package missing keys: "
                f"{sorted(missing)}"
            )

    return _model_package


# =========================================================
# MODEL INFORMATION
# =========================================================

def get_model_info() -> dict:
    """
    Return information about the trained AI model.
    """

    package = get_model_package()

    return {
        "status": "loaded",
        "model_type": type(
            package["model"]
        ).__name__,
        "model_version": package[
            "model_version"
        ],
        "target": package["target"],
        "features": package["features"],
        "model_path": str(
            MODEL_PATH
        ),
    }


# =========================================================
# POWER PREDICTION
# =========================================================

def predict_power(
    *,
    wind_speed: float,
    wind_direction: float,
    rpm: float,
    temperature: float,
    humidity: float,
    flap_angle: float,
) -> float:
    """
    Predict turbine power.

    flap_angle represents the average physical
    flap angle of the three turbine flaps.
    """

    package = get_model_package()

    model = package["model"]
    features = package["features"]

    values = {
        "wind_speed": float(
            wind_speed
        ),
        "wind_direction": float(
            wind_direction
        ),
        "rpm": float(
            rpm
        ),
        "temperature": float(
            temperature
        ),
        "humidity": float(
            humidity
        ),
        "flap_angle": float(
            flap_angle
        ),
    }

    missing = [
        feature
        for feature in features
        if feature not in values
    ]

    if missing:
        raise ValueError(
            "Missing model features: "
            f"{missing}"
        )

    row = {
        feature: values[feature]
        for feature in features
    }

    dataframe = pd.DataFrame(
        [row],
        columns=features,
    )

    prediction = model.predict(
        dataframe
    )

    return round(
        float(prediction[0]),
        2,
    )


# =========================================================
# THREE-FLAP PREDICTION
# =========================================================

def predict_power_for_flaps(
    *,
    wind_speed: float,
    wind_direction: float,
    rpm: float,
    temperature: float,
    humidity: float,
    flap_angle_1: float,
    flap_angle_2: float,
    flap_angle_3: float,
) -> float:
    """
    Predict power for the physical three-flap turbine.

    The trained model expects one flap_angle, so we use
    the average of the three physical flap angles.
    """

    average_flap = (
        float(flap_angle_1)
        + float(flap_angle_2)
        + float(flap_angle_3)
    ) / 3.0

    return predict_power(
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        rpm=rpm,
        temperature=temperature,
        humidity=humidity,
        flap_angle=average_flap,
    )


# =========================================================
# AI FLAP OPTIMIZER
# =========================================================

def find_best_flap_angle(
    *,
    wind_speed: float,
    wind_direction: float,
    rpm: float,
    temperature: float,
    humidity: float,
    current_flap_angle: float,
    minimum_angle: float = 5.0,
    maximum_angle: float = 35.0,
    step: float = 1.0,
) -> dict:
    """
    Test candidate flap angles from 5° to 35°.

    For every candidate angle the trained Random Forest
    predicts the resulting turbine power.

    The highest predicted-power SAFE angle is selected.
    """

    candidates = []

    angle = float(
        minimum_angle
    )

    while angle <= maximum_angle + 0.001:

        predicted_power = predict_power(
            wind_speed=wind_speed,
            wind_direction=wind_direction,
            rpm=rpm,
            temperature=temperature,
            humidity=humidity,
            flap_angle=angle,
        )

        candidates.append(
            {
                "angle": round(
                    angle,
                    1,
                ),
                "predicted_power_w": (
                    predicted_power
                ),
            }
        )

        angle += step

    best = max(
        candidates,
        key=lambda item:
        item["predicted_power_w"],
    )

    current_power = predict_power(
        wind_speed=wind_speed,
        wind_direction=wind_direction,
        rpm=rpm,
        temperature=temperature,
        humidity=humidity,
        flap_angle=current_flap_angle,
    )

    expected_gain = 0.0

    if current_power > 0:
        expected_gain = (
            (
                best["predicted_power_w"]
                - current_power
            )
            / current_power
        ) * 100.0

    return {
        "recommended_angle": best[
            "angle"
        ],

        "current_angle": round(
            current_flap_angle,
            1,
        ),

        "current_predicted_power_w": round(
            current_power,
            2,
        ),

        "predicted_power_w": best[
            "predicted_power_w"
        ],

        "expected_power_gain_percent": round(
            expected_gain,
            2,
        ),

        "candidates": candidates,

        "model_version": get_model_package()[
            "model_version"
        ],

        "controller_type": (
            "ml-random-forest"
        ),
    }