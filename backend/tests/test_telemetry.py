"""
FILE: backend/tests/test_telemetry.py

Covers:
- telemetry validation
- server-side power calculation
- latest telemetry
- authentication

RUN:
    pytest tests/test_telemetry.py -v
"""

SAMPLE_TELEMETRY = {
    "device_id": "WIND-TEST-001",
    "wind_speed": 8.4,
    "wind_direction": 145,
    "rpm": 412,
    "voltage": 18.7,
    "current": 2.4,
    "flap_angle_1": 15,
    "flap_angle_2": 15,
    "flap_angle_3": 15,
    "temperature": 31.5,
    "humidity": 62,
    "mode": "adaptive",
}


def test_post_telemetry_requires_auth(client):
    response = client.post(
        "/api/v1/telemetry",
        json=SAMPLE_TELEMETRY,
    )

    assert response.status_code == 401


def test_post_telemetry_success_and_power_calculation(
    client,
    auth_headers,
):
    response = client.post(
        "/api/v1/telemetry",
        json=SAMPLE_TELEMETRY,
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "stored"

    # P = V × I = 18.7 × 2.4 = 44.88 W
    assert abs(
        body["calculated_power_watts"] - 44.88
    ) < 0.001


def test_post_telemetry_rejects_out_of_range_wind_speed(
    client,
    auth_headers,
):
    bad_payload = {
        **SAMPLE_TELEMETRY,
        "wind_speed": 9999,
    }

    response = client.post(
        "/api/v1/telemetry",
        json=bad_payload,
        headers=auth_headers,
    )

    assert response.status_code == 422


def test_get_latest_telemetry_not_found(client):
    response = client.get(
        "/api/v1/telemetry/latest",
        params={
            "device_id": "NO-SUCH-DEVICE",
        },
    )

    assert response.status_code == 404


def test_get_latest_telemetry_after_post(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/telemetry",
        json=SAMPLE_TELEMETRY,
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/telemetry/latest",
        params={
            "device_id": "WIND-TEST-001",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["device_id"] == "WIND-TEST-001"
    assert body["power"] > 0


def test_get_telemetry_history(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/telemetry",
        json=SAMPLE_TELEMETRY,
        headers=auth_headers,
    )

    response = client.get(
        "/api/v1/telemetry/history",
        params={
            "device_id": "WIND-TEST-001",
            "hours": 24,
        },
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
