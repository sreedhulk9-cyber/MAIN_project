import pytest
from datetime import date, timedelta
from services.flight_provider import (
    DemoFlightProvider,
    validate_search_params,
    sort_flight_offers,
    get_flight_provider
)


def test_validate_search_params_success():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    origin_iata, dest_iata = validate_search_params("Kochi", "Delhi", tomorrow)
    assert origin_iata == "COK"
    assert dest_iata == "DEL"


def test_validate_search_params_same_airports_rejected():
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="Origin and destination cannot be the same"):
        validate_search_params("COK", "COK", tomorrow)


def test_validate_search_params_past_date_rejected():
    past_date = (date.today() - timedelta(days=5)).isoformat()
    with pytest.raises(ValueError, match="cannot be in the past"):
        validate_search_params("COK", "DEL", past_date)


def test_validate_search_params_return_before_departure_rejected():
    dep_date = (date.today() + timedelta(days=5)).isoformat()
    ret_date = (date.today() + timedelta(days=2)).isoformat()
    with pytest.raises(ValueError, match="cannot be before departure date"):
        validate_search_params("COK", "DEL", dep_date, ret_date)


def test_demo_flight_provider_search():
    provider = DemoFlightProvider()
    dep_date = (date.today() + timedelta(days=10)).isoformat()
    response = provider.search(
        origin="Kochi",
        destination="Delhi",
        departure_date=dep_date,
        adults=2,
        travel_class="ECONOMY",
        direct_only=False,
        sort_by="cheapest"
    )

    assert response.results_count > 0
    assert response.is_live is False
    assert "DEMO DATA" in response.source
    assert response.cheapest_flight is not None

    for flight in response.flights:
        assert flight.is_demo is True
        assert flight.price > 0
        assert flight.origin == "COK"
        assert flight.destination == "DEL"


def test_sorting_flight_offers():
    provider = DemoFlightProvider()
    dep_date = (date.today() + timedelta(days=10)).isoformat()
    response = provider.search("COK", "BLR", dep_date)

    cheapest_sorted = sort_flight_offers(response.flights, sort_by="cheapest")
    for i in range(len(cheapest_sorted) - 1):
        assert cheapest_sorted[i].price <= cheapest_sorted[i + 1].price

    fastest_sorted = sort_flight_offers(response.flights, sort_by="fastest")
    for i in range(len(fastest_sorted) - 1):
        assert fastest_sorted[i].duration_minutes <= fastest_sorted[i + 1].duration_minutes
