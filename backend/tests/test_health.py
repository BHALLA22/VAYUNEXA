"""
FILE: backend/tests/test_health.py

RUN:
    pytest tests/test_health.py -v
"""


def test_health_check(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["service"] == "vayunexa-backend"
