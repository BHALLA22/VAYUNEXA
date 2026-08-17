"""
FILE: backend/tests/test_energy.py

Covers:
- current power
- today's energy
- trapezoidal integration correctness

RUN:
    pytest tests/test_energy.py -v
"""

import datetime as dt


def _telemetry(
    device_id,
    wind_speed,
    voltage,
    current,
    minutes_ago,
    mode="adaptive",
):
    timestamp = (
        dt.datetime.now(dt.timezone.utc)
        - dt.timedelta(minutes=minutes_ago)
    ).isoformat()

    return {
        "device_id": device_id,
        "timestamp": timestamp,
        "wind_speed": wind_speed,
        "rpm": 300,
        "voltage": voltage,
        "current": current,
        "flap_angle_1": 15,
        "flap_angle_2": 15,
        "flap_angle_3": 15,
        "mode": mode,
    }


def test_current_power_reflects_latest_reading(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/telemetry",
        json=_telemetry(
            "WIND-E1",
            8,
            20,
            2,
            minutes_ago=5,
        ),
        headers=auth_headers,
    )

    client.post(
        "/api/v1/telemetry",
        json=_telemetry(
            "WIND-E1",
            9,
            20,
            3,
            minutes_ago=0,
        ),
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/energy/current",
        params={
            "device_id": "WIND-E1",
        },
    )

    assert response.status_code == 200

    # Latest reading: 20 V × 3 A = 60 W
    assert abs(
        response.json()["power_watts"] - 60.0
    ) < 0.001


def test_energy_today_returns_zero_with_no_data(client):
    response = client.get(
        "/api/v1/energy/today",
        params={
            "device_id": "NO-DATA-DEVICE",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["gross_energy_wh"] == 0
    assert body["sample_count"] == 0


def test_energy_today_integrates_two_points(
    client,
    auth_headers,
):
    # Two readings 30 minutes apart at constant 100 W.
    # Expected:
    # 100 W × 0.5 h = 50 Wh

    client.post(
        "/api/v1/telemetry",
        json=_telemetry(
            "WIND-E2",
            8,
            10,
            10,
            minutes_ago=30,
        ),
        headers=auth_headers,
    )

    client.post(
        "/api/v1/telemetry",
        json=_telemetry(
            "WIND-E2",
            8,
            10,
            10,
            minutes_ago=0,
        ),
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/energy/today",
        params={
            "device_id": "WIND-E2",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert abs(
        body["gross_energy_wh"] - 50.0
    ) < 0.5
