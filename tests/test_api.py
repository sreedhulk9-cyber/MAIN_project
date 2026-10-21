import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "calculator" in data["registered_agents"]
    assert "researcher" in data["registered_agents"]
    assert "flight_agent" in data["registered_agents"]


def test_airports_search_endpoint():
    res = client.get("/api/airports/search?q=Kochi")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert data[0]["iata"] == "COK"


def test_flight_search_endpoint_valid():
    tomorrow = (date.today() + timedelta(days=5)).isoformat()
    payload = {
        "origin": "COK",
        "destination": "DEL",
        "departure_date": tomorrow,
        "adults": 1,
        "travel_class": "ECONOMY",
        "direct_only": False,
        "sort_by": "cheapest"
    }
    res = client.post("/api/flights/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["results_count"] > 0
    assert len(data["flights"]) > 0
    assert data["flights"][0]["origin"] == "COK"
    assert data["flights"][0]["destination"] == "DEL"


def test_flight_search_endpoint_invalid_past_date():
    past = (date.today() - timedelta(days=2)).isoformat()
    payload = {
        "origin": "COK",
        "destination": "DEL",
        "departure_date": past,
        "adults": 1
    }
    res = client.post("/api/flights/search", json=payload)
    assert res.status_code == 400
    assert "cannot be in the past" in res.json()["detail"]


def test_flight_search_endpoint_same_route():
    tomorrow = (date.today() + timedelta(days=5)).isoformat()
    payload = {
        "origin": "COK",
        "destination": "COK",
        "departure_date": tomorrow
    }
    res = client.post("/api/flights/search", json=payload)
    assert res.status_code == 400
    assert "Origin and destination cannot be the same" in res.json()["detail"]
