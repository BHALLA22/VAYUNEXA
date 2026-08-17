"""
FILE: backend/tests/test_safety_validation.py

PURPOSE:
Backend-side validation of physically impossible or unsafe values.

NOTE:
This does NOT replace firmware-side safety validation.
The ESP8266 must independently validate any flap command.
"""

BASE = {
    "device_id": "WIND-SAFE-1",
    "wind_speed": 8,
    "rpm": 300,
    "voltage": 12,
    "current": 1,
    "flap_angle_1": 10,
    "flap_angle_2": 10,
    "flap_angle_3": 10,
    "mode": "adaptive",
}


def test_rejects_flap_angle_above_90(
    client,
    auth_headers,
):
    payload = {
        **BASE,
        "flap_angle_1": 150,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_rejects_negative_flap_angle(
    client,
    auth_headers,
):
    payload = {
        **BASE,
        "flap_angle_2": -5,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_rejects_negative_rpm(
    client,
    auth_headers,
):
    payload = {
        **BASE,
        "rpm": -100,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_accepts_valid_boundary_values(
    client,
    auth_headers,
):
    payload = {
        **BASE,
        "flap_angle_1": 90,
        "flap_angle_2": 0,
        "flap_angle_3": 45,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
