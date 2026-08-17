"""
VAYUNEXA AI Automatic Flap Controller

CONTROL PIPELINE

    Latest telemetry
          |
          v
    Random Forest AI
          |
          v
    Test flap angles 5° -> 35°
          |
          v
    Select highest predicted power
          |
          v
    Mechanical safety limits
          |
          v
    Maximum movement per cycle
          |
          v
    Final flap targets

The AI model is vayu-rf-v1.

IMPORTANT:
The current trained model expects one flap_angle feature.
For the physical three-flap turbine, the same optimized angle
is initially applied to all three flaps.

The safety layer remains independent of the AI.
"""

from dataclasses import dataclass

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.telemetry import Telemetry
from app.services.ai_prediction_service import (
    find_best_flap_angle,
)


# ============================================================
# SAFETY CONFIGURATION
# ============================================================

MIN_FLAP_ANGLE = 5.0
MAX_FLAP_ANGLE = 35.0

# Maximum physical movement during one control cycle.
MAX_ANGLE_CHANGE_PER_STEP = 5.0


# ============================================================
# CONTROL DECISION
# ============================================================

@dataclass
class ControlDecision:

    device_id: str

    current_angles: tuple[
        float,
        float,
        float,
    ]

    target_angles: tuple[
        float,
        float,
        float,
    ]

    reason: str

    expected_power_gain_percent: float

    safe: bool

    predicted_current_power_w: float

    predicted_target_power_w: float

    recommended_angle: float

    controller_type: str

    model_version: str


# ============================================================
# SAFETY FUNCTIONS
# ============================================================

def clamp_angle(
    angle: float,
) -> float:
    """
    Keep an angle inside the physical flap range.
    """

    return max(
        MIN_FLAP_ANGLE,
        min(
            MAX_FLAP_ANGLE,
            float(angle),
        ),
    )


def limit_angle_change(
    current: float,
    target: float,
) -> float:
    """
    Prevent excessively large flap movement in one
    control cycle.
    """

    difference = target - current

    if difference > MAX_ANGLE_CHANGE_PER_STEP:

        return (
            current
            + MAX_ANGLE_CHANGE_PER_STEP
        )

    if difference < -MAX_ANGLE_CHANGE_PER_STEP:

        return (
            current
            - MAX_ANGLE_CHANGE_PER_STEP
        )

    return target


# ============================================================
# AI CONTROL DECISION
# ============================================================

def calculate_control_decision(
    db: Session,
    device_id: str,
) -> ControlDecision:
    """
    Calculate the next AI-controlled flap positions.

    Steps:

    1. Read latest telemetry.
    2. Calculate current average flap angle.
    3. Send live environmental conditions to the
       Random Forest optimizer.
    4. Test candidate flap angles.
    5. Select the angle with highest predicted power.
    6. Apply mechanical safety limits.
    7. Limit movement to 5° per control cycle.
    8. Return the final command.
    """

    # --------------------------------------------------------
    # 1. GET LATEST TELEMETRY
    # --------------------------------------------------------

    latest = db.execute(
        select(Telemetry)
        .where(
            Telemetry.device_id == device_id
        )
        .order_by(
            desc(Telemetry.timestamp)
        )
        .limit(1)
    ).scalar_one_or_none()

    if latest is None:

        raise ValueError(
            f"No telemetry available for {device_id}"
        )

    # --------------------------------------------------------
    # 2. CURRENT FLAP POSITIONS
    # --------------------------------------------------------

    current_angles = (
        float(
            latest.flap_angle_1
        ),
        float(
            latest.flap_angle_2
        ),
        float(
            latest.flap_angle_3
        ),
    )

    current_average = (
        current_angles[0]
        + current_angles[1]
        + current_angles[2]
    ) / 3.0

    # --------------------------------------------------------
    # 3. RUN RANDOM FOREST AI
    # --------------------------------------------------------

    ai_result = find_best_flap_angle(

        wind_speed=float(
            latest.wind_speed
        ),

        wind_direction=float(
            latest.wind_direction
        ),

        rpm=float(
            latest.rpm
        ),

        temperature=float(
            latest.temperature
        ),

        humidity=float(
            latest.humidity
        ),

        current_flap_angle=current_average,

        minimum_angle=MIN_FLAP_ANGLE,

        maximum_angle=MAX_FLAP_ANGLE,

        step=1.0,
    )

    # --------------------------------------------------------
    # 4. AI RECOMMENDED ANGLE
    # --------------------------------------------------------

    recommended_angle = clamp_angle(
        float(
            ai_result[
                "recommended_angle"
            ]
        )
    )

    # --------------------------------------------------------
    # 5. LIMIT PHYSICAL MOVEMENT
    # --------------------------------------------------------

    target_1 = limit_angle_change(
        current_angles[0],
        recommended_angle,
    )

    target_2 = limit_angle_change(
        current_angles[1],
        recommended_angle,
    )

    target_3 = limit_angle_change(
        current_angles[2],
        recommended_angle,
    )

    # --------------------------------------------------------
    # 6. FINAL SAFETY CLAMP
    # --------------------------------------------------------

    target_angles = (
        clamp_angle(target_1),
        clamp_angle(target_2),
        clamp_angle(target_3),
    )

    # --------------------------------------------------------
    # 7. SAFETY VALIDATION
    # --------------------------------------------------------

    safe = all(
        MIN_FLAP_ANGLE
        <= angle
        <= MAX_FLAP_ANGLE
        for angle in target_angles
    )

    if not safe:

        raise ValueError(
            "AI generated an unsafe flap command."
        )

    # --------------------------------------------------------
    # 8. AI EXPLANATION
    # --------------------------------------------------------

    reason = (
        "Random Forest AI selected "
        f"{recommended_angle:.1f}° because it "
        "produced the highest predicted power "
        f"of {ai_result['predicted_power_w']:.2f} W "
        "among the tested safe flap angles."
    )

    # --------------------------------------------------------
    # 9. RETURN CONTROL DECISION
    # --------------------------------------------------------

    return ControlDecision(

        device_id=device_id,

        current_angles=current_angles,

        target_angles=target_angles,

        reason=reason,

        expected_power_gain_percent=float(
            ai_result[
                "expected_power_gain_percent"
            ]
        ),

        safe=safe,

        predicted_current_power_w=float(
            ai_result[
                "current_predicted_power_w"
            ]
        ),

        predicted_target_power_w=float(
            ai_result[
                "predicted_power_w"
            ]
        ),

        recommended_angle=recommended_angle,

        controller_type=str(
            ai_result[
                "controller_type"
            ]
        ),

        model_version=str(
            ai_result[
                "model_version"
            ]
        ),
    )