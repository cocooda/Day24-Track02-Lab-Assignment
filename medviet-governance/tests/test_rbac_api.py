from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_missing_token_returns_401():
    response = client.get("/api/patients/raw")
    assert response.status_code == 401


def test_invalid_token_returns_401():
    response = client.get("/api/patients/raw", headers=auth_header("bad-token"))
    assert response.status_code == 401


def test_bob_cannot_read_raw_patients():
    response = client.get("/api/patients/raw", headers=auth_header("token-bob"))
    assert response.status_code == 403


def test_alice_can_read_raw_patients():
    response = client.get("/api/patients/raw", headers=auth_header("token-alice"))
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_bob_can_read_anonymized_patients():
    response = client.get("/api/patients/anonymized", headers=auth_header("token-bob"))
    assert response.status_code == 200
    assert len(response.json()) == 10


def test_carol_can_read_aggregated_metrics():
    response = client.get("/api/metrics/aggregated", headers=auth_header("token-carol"))
    assert response.status_code == 200
    body = response.json()
    assert "disease_counts" in body


def test_dave_cannot_access_production_endpoints():
    response = client.get("/api/metrics/aggregated", headers=auth_header("token-dave"))
    assert response.status_code == 403


def test_bob_cannot_delete_patient():
    response = client.delete("/api/patients/patient-1", headers=auth_header("token-bob"))
    assert response.status_code == 403


def test_alice_can_delete_patient():
    response = client.delete("/api/patients/patient-1", headers=auth_header("token-alice"))
    assert response.status_code == 200
    assert response.json()["deleted"] is True
