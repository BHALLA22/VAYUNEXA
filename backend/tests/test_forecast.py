"""
FILE: backend/tests/test_forecast.py

Covers:
- forecast endpoints
- heuristic fallback path
- 24h / 48h / 72h / 96h horizons
- model metrics when no trained model exists
"""

SAMPLE_TELEMETRY = {
    "device_id": "WIND-F1",
    "wind_speed": 8.4,
    "rpm": 412,
    "voltage": 18.7,
    "current": 2.4,
    "flap_angle_1": 15,
    "flap_angle_2": 15,
    "flap_angle_3": 15,
    "mode": "adaptive",
}


def test_forecast_24h_without_any_telemetry_still_responds(client):
    response = client.get(
        "/api/v1/forecast/24h",
        params={"device_id": "NEVER-SEEN"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["horizon_hours"] == 24
    assert len(body["points"]) == 24
    assert body["is_ai_model"] is False


def test_forecast_horizons_return_correct_point_counts(
    client,
    auth_headers,
):
    client.post(
        "/api/v1/telemetry",
        json=SAMPLE_TELEMETRY,
        headers=auth_headers,
    )

    for horizon, path in [
        (24, "24h"),
        (48, "48h"),
        (72, "72h"),
        (96, "96h"),
    ]:
        response = client.get(
            f"/api/v1/forecast/{path}",
            params={"device_id": "WIND-F1"},
        )

        assert response.status_code == 200
        assert len(response.json()["points"]) == horizon


def test_model_metrics_reports_no_model_when_untrained(client):
    response = client.get("/api/v1/model/metrics")

    assert response.status_code == 200
    assert response.json()["status"] == "no_trained_model_yet"
