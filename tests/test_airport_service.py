import pytest
from services.airport_service import lookup_iata, get_airport_info, search_airports


def test_iata_lookup_exact_code():
    assert lookup_iata("COK") == "COK"
    assert lookup_iata("DEL") == "DEL"
    assert lookup_iata("BLR") == "BLR"
    assert lookup_iata("DXB") == "DXB"


def test_iata_lookup_city_names():
    assert lookup_iata("Kochi") == "COK"
    assert lookup_iata("Cochin") == "COK"
    assert lookup_iata("Delhi") == "DEL"
    assert lookup_iata("New Delhi") == "DEL"
    assert lookup_iata("Bangalore") == "BLR"
    assert lookup_iata("Bengaluru") == "BLR"
    assert lookup_iata("Mumbai") == "BOM"
    assert lookup_iata("Dubai") == "DXB"


def test_search_airports_autocomplete():
    results = search_airports("Koch")
    assert len(results) > 0
    assert any(r["iata"] == "COK" for r in results)

    results_delhi = search_airports("DEL")
    assert len(results_delhi) > 0
    assert results_delhi[0]["iata"] == "DEL"


def test_get_airport_info():
    info = get_airport_info("COK")
    assert info is not None
    assert info["city"] == "Kochi"
    assert info["iata"] == "COK"
