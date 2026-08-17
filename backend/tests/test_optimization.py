"""
FILE: backend/tests/test_optimization.py

Covers:
- optimization recommendation
- wind-speed bands
- safe default
"""


def _post(
    client,
    auth_headers,
    device_id,
    wind_speed,
):
    client.post(
        "/api/v1/telemetry",
        json={
            "device_id": device_id,
            "wind_speed": wind_speed,
            "rpm": 300,
            "voltage": 12,
            "current": 1,
            "flap_angle_1": 10,
            "flap_angle_2": 10,
            "flap_angle_3": 10,
            "mode": "adaptive",
        },
        headers=auth_headers,
    )


def test_recommendation_with_no_data_returns_safe_default(client):
    response = client.get(
        "/api/v1/optimization/recommendation",
        params={"device_id": "NEVER-SEEN"},
    )

    assert response.status_code == 200
    assert response.json()["recommended_angle"] >= 0


def test_recommendation_low_wind_gives_small_angle(
    client,
    auth_headers,
):
    _post(
        client,
        auth_headers,
        "WIND-O1",
        wind_speed=3.0,
    )

    response = client.get(
        "/api/v1/optimization/recommendation",
        params={"device_id": "WIND-O1"},
    )

    body = response.json()

    assert body["recommended_angle"] <= 10


def test_recommendation_high_wind_gives_large_angle_for_protection(
    client,
    auth_headers,
):
    _post(
        client,
        auth_headers,
        "WIND-O2",
        wind_speed=20.0,
    )

    response = client.get(
        "/api/v1/optimization/recommendation",
        params={"device_id": "WIND-O2"},
    )

    body = response.json()

    assert body["recommended_angle"] >= 30
    assert body["is_experimental_estimate"] is True
