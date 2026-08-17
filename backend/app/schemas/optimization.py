"""
FILE: backend/app/schemas/optimization.py

PURPOSE:
Pydantic schema for the flap-angle optimization recommendation
returned to the ESP8266 and dashboard.
"""

from pydantic import BaseModel


class OptimizationRecommendation(BaseModel):
    device_id: str
    recommended_angle: float
    current_angle_avg: float
    reason: str
    expected_power_gain_percent: float
    is_experimental_estimate: bool = True
    controller_version: str = "baseline-rule-v1"
