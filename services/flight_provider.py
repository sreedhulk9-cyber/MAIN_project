"""Modular flight provider service supporting Amadeus API, Duffel API, and Transparent Demo Mode."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
import os
import re
import requests

from services.airport_service import lookup_iata, get_airport_info


@dataclass
class FlightSegment:
    carrier_code: str
    carrier_name: str
    flight_number: str
    departure_airport: str
    departure_city: str
    departure_time: str
    arrival_airport: str
    arrival_city: str
    arrival_time: str
    duration: str
    duration_minutes: int
    aircraft: Optional[str] = None


@dataclass
class FlightOffer:
    id: str
    airline: str
    airline_code: str
    flight_number: str
    origin: str
    origin_city: str
    destination: str
    destination_city: str
    departure_time: str
    arrival_time: str
    duration: str
    duration_minutes: int
    stops: int
    stop_airports: List[str] = field(default_factory=list)
    segments: List[Dict[str, Any]] = field(default_factory=list)
    price: float = 0.0
    currency: str = "INR"
    cabin_class: str = "ECONOMY"
    seats_available: Optional[int] = None
    booking_url: Optional[str] = None
    is_round_trip: bool = False
    return_flight: Optional[Dict[str, Any]] = None
    is_demo: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FlightSearchResponse:
    query: Dict[str, Any]
    results_count: int
    flights: List[FlightOffer]
    cheapest_flight: Optional[FlightOffer]
    fastest_flight: Optional[FlightOffer]
    is_live: bool
    source: str
    retrieved_at: str
    provider_name: str
    warning: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["flights"] = [f.to_dict() if hasattr(f, "to_dict") else f for f in self.flights]
        if self.cheapest_flight and hasattr(self.cheapest_flight, "to_dict"):
            data["cheapest_flight"] = self.cheapest_flight.to_dict()
        if self.fastest_flight and hasattr(self.fastest_flight, "to_dict"):
            data["fastest_flight"] = self.fastest_flight.to_dict()
        return data


def parse_iso_duration(duration_str: str) -> (str, int):
    """
    Parse ISO 8601 duration string (e.g., 'PT3H15M' or 'PT45M') to ('3h 15m', 195).
    """
    if not duration_str or not duration_str.startswith("PT"):
        return duration_str or "N/A", 0

    hours_match = re.search(r"(\d+)H", duration_str)
    minutes_match = re.search(r"(\d+)M", duration_str)

    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    total_minutes = hours * 60 + minutes
    formatted = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
    return formatted, total_minutes


def validate_search_params(origin: str, destination: str, departure_date_str: str, return_date_str: Optional[str] = None):
    """Validate core flight search parameters, raising ValueError with friendly messages."""
    if not origin or not destination:
        raise ValueError("Both origin and destination airports/cities are required.")

    origin_iata = lookup_iata(origin)
    if not origin_iata:
        raise ValueError(f"Could not identify airport for origin '{origin}'. Please provide a valid city name or 3-letter IATA code.")

    dest_iata = lookup_iata(destination)
    if not dest_iata:
        raise ValueError(f"Could not identify airport for destination '{destination}'. Please provide a valid city name or 3-letter IATA code.")

    if origin_iata == dest_iata:
        raise ValueError("Origin and destination cannot be the same airport.")

    try:
        dep_date = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid departure date format '{departure_date_str}'. Expected format is YYYY-MM-DD.")

    today = date.today()
    if dep_date < today:
        raise ValueError(f"Departure date ({departure_date_str}) cannot be in the past. Today is {today.isoformat()}.")

    if return_date_str:
        try:
            ret_date = datetime.strptime(return_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid return date format '{return_date_str}'. Expected format is YYYY-MM-DD.")

        if ret_date < dep_date:
            raise ValueError(f"Return date ({return_date_str}) cannot be before departure date ({departure_date_str}).")

    return origin_iata, dest_iata


class BaseFlightProvider(ABC):
    """Abstract base class for all flight providers."""

    @abstractmethod
    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: str = "ECONOMY",
        direct_only: bool = False,
        sort_by: str = "cheapest"
    ) -> FlightSearchResponse:
        pass


class AmadeusFlightProvider(BaseFlightProvider):
    """Real flight search integration with Amadeus Flight Offers API (v2)."""

    def __init__(self, client_id: str, client_secret: str, is_production: bool = False):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.amadeus.com" if is_production else "https://test.api.amadeus.com"
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_access_token(self) -> str:
        """Fetch or refresh OAuth2 client credentials bearer token."""
        if self._access_token and self._token_expires_at and datetime.now() < self._token_expires_at:
            return self._access_token

        token_url = f"{self.base_url}/v1/security/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = requests.post(token_url, data=payload, headers=headers, timeout=12)
        if response.status_code != 200:
            raise RuntimeError(f"Amadeus authentication failed ({response.status_code}): {response.text}")

        data = response.json()
        self._access_token = data.get("access_token")
        expires_in = data.get("expires_in", 1799)
        self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
        return self._access_token

    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: str = "ECONOMY",
        direct_only: bool = False,
        sort_by: str = "cheapest"
    ) -> FlightSearchResponse:
        origin_iata, dest_iata = validate_search_params(origin, destination, departure_date, return_date)
        token = self._get_access_token()

        search_url = f"{self.base_url}/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }

        # Determine currency default
        currency = "INR" if origin_iata in ["COK", "DEL", "BOM", "BLR", "MAA", "CCU", "HYD", "GOI"] else "USD"

        params: Dict[str, Any] = {
            "originLocationCode": origin_iata,
            "destinationLocationCode": dest_iata,
            "departureDate": departure_date,
            "adults": max(1, min(adults, 9)),
            "travelClass": travel_class.upper(),
            "currencyCode": currency,
            "max": 25
        }

        if direct_only:
            params["nonStop"] = "true"

        if return_date:
            params["returnDate"] = return_date

        response = requests.get(search_url, headers=headers, params=params, timeout=18)

        if response.status_code != 200:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            detail = error_data.get("errors", [{}])[0].get("detail", response.text)
            raise RuntimeError(f"Amadeus API search failed ({response.status_code}): {detail}")

        payload = response.json()
        raw_offers = payload.get("data", [])
        carriers_dict = payload.get("dictionaries", {}).get("carriers", {})

        flights: List[FlightOffer] = []
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        for idx, offer in enumerate(raw_offers):
            itineraries = offer.get("itineraries", [])
            if not itineraries:
                continue

            outbound = itineraries[0]
            segments = outbound.get("segments", [])
            if not segments:
                continue

            first_seg = segments[0]
            last_seg = segments[-1]

            carrier_code = first_seg.get("carrierCode", "XX")
            airline_name = carriers_dict.get(carrier_code, carrier_code)
            flight_num = f"{carrier_code}-{first_seg.get('number', '')}"

            dep_time = first_seg.get("departure", {}).get("at", "")
            arr_time = last_seg.get("arrival", {}).get("at", "")
            raw_duration = outbound.get("duration", "")
            duration_formatted, duration_mins = parse_iso_duration(raw_duration)

            stops = len(segments) - 1
            stop_airports = [s.get("departure", {}).get("iataCode") for s in segments[1:]]

            total_price_str = offer.get("price", {}).get("total", "0.0")
            price_val = float(total_price_str)
            curr = offer.get("price", {}).get("currency", currency)

            # Build parsed segments
            parsed_segments = []
            for seg in segments:
                seg_carrier = seg.get("carrierCode", "")
                parsed_segments.append({
                    "carrier_code": seg_carrier,
                    "carrier_name": carriers_dict.get(seg_carrier, seg_carrier),
                    "flight_number": f"{seg_carrier}-{seg.get('number', '')}",
                    "departure_airport": seg.get("departure", {}).get("iataCode", ""),
                    "departure_time": seg.get("departure", {}).get("at", ""),
                    "arrival_airport": seg.get("arrival", {}).get("iataCode", ""),
                    "arrival_time": seg.get("arrival", {}).get("at", ""),
                    "duration": parse_iso_duration(seg.get("duration", ""))[0]
                })

            # Check if return flight exists
            return_offer_data = None
            if len(itineraries) > 1 and return_date:
                inbound = itineraries[1]
                in_segments = inbound.get("segments", [])
                if in_segments:
                    in_first = in_segments[0]
                    in_last = in_segments[-1]
                    in_carrier = in_first.get("carrierCode", "")
                    in_duration, _ = parse_iso_duration(inbound.get("duration", ""))
                    return_offer_data = {
                        "airline": carriers_dict.get(in_carrier, in_carrier),
                        "airline_code": in_carrier,
                        "flight_number": f"{in_carrier}-{in_first.get('number', '')}",
                        "departure_time": in_first.get("departure", {}).get("at", ""),
                        "arrival_time": in_last.get("arrival", {}).get("at", ""),
                        "duration": in_duration,
                        "stops": len(in_segments) - 1
                    }

            flight_obj = FlightOffer(
                id=str(offer.get("id", idx + 1)),
                airline=airline_name,
                airline_code=carrier_code,
                flight_number=flight_num,
                origin=origin_iata,
                origin_city=get_airport_info(origin_iata)["city"],
                destination=dest_iata,
                destination_city=get_airport_info(dest_iata)["city"],
                departure_time=dep_time,
                arrival_time=arr_time,
                duration=duration_formatted,
                duration_minutes=duration_mins,
                stops=stops,
                stop_airports=stop_airports,
                segments=parsed_segments,
                price=price_val,
                currency=curr,
                cabin_class=travel_class.upper(),
                seats_available=offer.get("numberOfBookableSeats"),
                booking_url=None,  # Amadeus self-service test mode does not issue direct booking URLs
                is_round_trip=bool(return_date),
                return_flight=return_offer_data,
                is_demo=False
            )
            flights.append(flight_obj)

        sorted_flights = sort_flight_offers(flights, sort_by)

        cheapest = min(sorted_flights, key=lambda f: f.price) if sorted_flights else None
        fastest = min(sorted_flights, key=lambda f: f.duration_minutes) if sorted_flights else None

        source_label = "Amadeus Flight Offers API (Live Environment)" if "api.amadeus.com" in self.base_url else "Amadeus Flight Offers API (Test Environment)"

        return FlightSearchResponse(
            query={
                "origin": origin_iata,
                "destination": dest_iata,
                "departure_date": departure_date,
                "return_date": return_date,
                "adults": adults,
                "travel_class": travel_class,
                "direct_only": direct_only,
                "sort_by": sort_by
            },
            results_count=len(sorted_flights),
            flights=sorted_flights,
            cheapest_flight=cheapest,
            fastest_flight=fastest,
            is_live=True,
            source=source_label,
            retrieved_at=now_iso,
            provider_name="Amadeus"
        )


class DuffelFlightProvider(BaseFlightProvider):
    """Real flight search integration with Duffel Air API."""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://api.duffel.com"

    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: str = "ECONOMY",
        direct_only: bool = False,
        sort_by: str = "cheapest"
    ) -> FlightSearchResponse:
        origin_iata, dest_iata = validate_search_params(origin, destination, departure_date, return_date)

        slices = [{"origin": origin_iata, "destination": dest_iata, "departure_date": departure_date}]
        if return_date:
            slices.append({"origin": dest_iata, "destination": origin_iata, "departure_date": return_date})

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Duffel-Version": "v2",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        duffel_cabin = travel_class.lower()
        if duffel_cabin not in ["economy", "premium_economy", "business", "first"]:
            duffel_cabin = "economy"

        payload = {
            "data": {
                "slices": slices,
                "passengers": [{"type": "adult"} for _ in range(max(1, adults))],
                "cabin_class": duffel_cabin,
                "return_offers": True
            }
        }

        url = f"{self.base_url}/air/offer_requests"
        resp = requests.post(url, json=payload, headers=headers, timeout=20)

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Duffel API error ({resp.status_code}): {resp.text}")

        data = resp.json().get("data", {})
        raw_offers = data.get("offers", [])

        flights: List[FlightOffer] = []
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        for idx, offer in enumerate(raw_offers):
            slices_data = offer.get("slices", [])
            if not slices_data:
                continue

            outbound_slice = slices_data[0]
            segments = outbound_slice.get("segments", [])
            if not segments:
                continue

            first_seg = segments[0]
            last_seg = segments[-1]

            carrier = offer.get("owner", {})
            airline_name = carrier.get("name", "Airline")
            airline_code = carrier.get("iata_code", "XX")
            flight_num = f"{airline_code}-{first_seg.get('marketing_carrier_flight_number', '101')}"

            dep_time = first_seg.get("departing_at", "")
            arr_time = last_seg.get("arriving_at", "")
            iso_dur = outbound_slice.get("duration", "")
            dur_fmt, dur_mins = parse_iso_duration(iso_dur)

            stops = len(segments) - 1
            if direct_only and stops > 0:
                continue

            price = float(offer.get("total_amount", "0"))
            curr = offer.get("total_currency", "INR")

            flight = FlightOffer(
                id=str(offer.get("id", idx + 1)),
                airline=airline_name,
                airline_code=airline_code,
                flight_number=flight_num,
                origin=origin_iata,
                origin_city=get_airport_info(origin_iata)["city"],
                destination=dest_iata,
                destination_city=get_airport_info(dest_iata)["city"],
                departure_time=dep_time,
                arrival_time=arr_time,
                duration=dur_fmt,
                duration_minutes=dur_mins,
                stops=stops,
                stop_airports=[s.get("origin", {}).get("iata_code") for s in segments[1:]],
                price=price,
                currency=curr,
                cabin_class=travel_class.upper(),
                booking_url=None,
                is_round_trip=bool(return_date),
                is_demo=False
            )
            flights.append(flight)

        sorted_flights = sort_flight_offers(flights, sort_by)

        return FlightSearchResponse(
            query={"origin": origin_iata, "destination": dest_iata, "departure_date": departure_date},
            results_count=len(sorted_flights),
            flights=sorted_flights,
            cheapest_flight=min(sorted_flights, key=lambda f: f.price) if sorted_flights else None,
            fastest_flight=min(sorted_flights, key=lambda f: f.duration_minutes) if sorted_flights else None,
            is_live=True,
            source="Duffel Air API",
            retrieved_at=now_iso,
            provider_name="Duffel"
        )


class DemoFlightProvider(BaseFlightProvider):
    """
    Transparent Fallback Demo Provider.
    ACTIVATED ONLY when live credentials (AMADEUS_CLIENT_ID or DUFFEL_API_KEY) are not set.
    Clearly marks all data as DEMO DATA in compliance with platform integrity guidelines.
    """

    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        travel_class: str = "ECONOMY",
        direct_only: bool = False,
        sort_by: str = "cheapest"
    ) -> FlightSearchResponse:
        origin_iata, dest_iata = validate_search_params(origin, destination, departure_date, return_date)

        origin_info = get_airport_info(origin_iata)
        dest_info = get_airport_info(dest_iata)
        now_iso = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Typical airlines by region
        is_indian = origin_iata in ["COK", "DEL", "BOM", "BLR", "MAA", "CCU", "HYD", "GOI"] and dest_iata in ["COK", "DEL", "BOM", "BLR", "MAA", "CCU", "HYD", "GOI"]
        is_gulf = dest_iata in ["DXB", "AUH", "SHJ", "DOH"] or origin_iata in ["DXB", "AUH", "SHJ", "DOH"]

        if is_gulf:
            airline_options = [
                {"name": "Emirates", "code": "EK", "base_price": 18500, "base_mins": 255},
                {"name": "Air India Express", "code": "IX", "base_price": 11200, "base_mins": 260},
                {"name": "IndiGo", "code": "6E", "base_price": 12800, "base_mins": 270},
                {"name": "Flydubai", "code": "FZ", "base_price": 14300, "base_mins": 265},
                {"name": "Air Arabia", "code": "G9", "base_price": 11900, "base_mins": 275},
            ]
            currency = "INR"
        elif is_indian:
            airline_options = [
                {"name": "IndiGo", "code": "6E", "base_price": 4900, "base_mins": 185},
                {"name": "Air India", "code": "AI", "base_price": 5400, "base_mins": 190},
                {"name": "Vistara", "code": "UK", "base_price": 6100, "base_mins": 180},
                {"name": "Akasa Air", "code": "QP", "base_price": 4450, "base_mins": 195},
                {"name": "SpiceJet", "code": "SG", "base_price": 4800, "base_mins": 200},
            ]
            currency = "INR"
        else:
            airline_options = [
                {"name": "British Airways", "code": "BA", "base_price": 42000, "base_mins": 560},
                {"name": "Lufthansa", "code": "LH", "base_price": 46500, "base_mins": 540},
                {"name": "Qatar Airways", "code": "QR", "base_price": 39000, "base_mins": 590},
                {"name": "Air France", "code": "AF", "base_price": 44200, "base_mins": 570},
            ]
            currency = "INR"

        multiplier = {"ECONOMY": 1.0, "PREMIUM_ECONOMY": 1.6, "BUSINESS": 2.8, "FIRST": 4.5}.get(travel_class.upper(), 1.0)
        passenger_multiplier = max(1, adults)

        departure_hours = ["06:15", "09:30", "13:45", "17:20", "20:40", "22:15"]
        demo_offers: List[FlightOffer] = []

        for i, carrier in enumerate(airline_options):
            dep_clock = departure_hours[i % len(departure_hours)]
            dep_hour, dep_min = map(int, dep_clock.split(":"))

            is_direct = (i % 3 != 2)  # Some flights 1-stop
            if direct_only and not is_direct:
                continue

            stops = 0 if is_direct else 1
            stop_airport = ["BOM" if origin_iata != "BOM" and dest_iata != "BOM" else "DEL"] if stops > 0 else []

            flight_mins = carrier["base_mins"] + (0 if is_direct else 115)
            hours_dur = flight_mins // 60
            mins_dur = flight_mins % 60
            dur_str = f"{hours_dur}h {mins_dur}m"

            dep_dt = datetime.strptime(f"{departure_date}T{dep_clock}:00", "%Y-%m-%dT%H:%M:%S")
            arr_dt = dep_dt + timedelta(minutes=flight_mins)

            flight_num = f"{carrier['code']}-{100 + (i * 73) % 900}"
            price = round((carrier["base_price"] * multiplier * (0.95 if is_direct else 0.88)) * passenger_multiplier, 2)

            return_offer = None
            if return_date:
                ret_dep_dt = datetime.strptime(f"{return_date}T{departure_hours[(i + 2) % len(departure_hours)]}:00", "%Y-%m-%dT%H:%M:%S")
                ret_arr_dt = ret_dep_dt + timedelta(minutes=flight_mins)
                return_offer = {
                    "airline": carrier["name"],
                    "airline_code": carrier["code"],
                    "flight_number": f"{carrier['code']}-{200 + (i * 47) % 900}",
                    "departure_time": ret_dep_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "arrival_time": ret_arr_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "duration": dur_str,
                    "stops": stops
                }
                # Double price roughly for return
                price = round(price * 1.9, 2)

            segments = [
                {
                    "carrier_code": carrier["code"],
                    "carrier_name": carrier["name"],
                    "flight_number": flight_num,
                    "departure_airport": origin_iata,
                    "departure_time": dep_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                    "arrival_airport": dest_iata if is_direct else stop_airport[0],
                    "arrival_time": arr_dt.strftime("%Y-%m-%dT%H:%M:%S") if is_direct else (dep_dt + timedelta(minutes=90)).strftime("%Y-%m-%dT%H:%M:%S"),
                    "duration": dur_str if is_direct else "1h 30m"
                }
            ]

            offer = FlightOffer(
                id=f"DEMO-FLIGHT-{i+1}",
                airline=carrier["name"],
                airline_code=carrier["code"],
                flight_number=flight_num,
                origin=origin_iata,
                origin_city=origin_info["city"],
                destination=dest_iata,
                destination_city=dest_info["city"],
                departure_time=dep_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                arrival_time=arr_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                duration=dur_str,
                duration_minutes=flight_mins,
                stops=stops,
                stop_airports=stop_airport,
                segments=segments,
                price=price,
                currency=currency,
                cabin_class=travel_class.upper(),
                seats_available=9 - i,
                booking_url=None,
                is_round_trip=bool(return_date),
                return_flight=return_offer,
                is_demo=True
            )
            demo_offers.append(offer)

        sorted_offers = sort_flight_offers(demo_offers, sort_by)

        return FlightSearchResponse(
            query={
                "origin": origin_iata,
                "destination": dest_iata,
                "departure_date": departure_date,
                "return_date": return_date,
                "adults": adults,
                "travel_class": travel_class,
                "direct_only": direct_only,
                "sort_by": sort_by
            },
            results_count=len(sorted_offers),
            flights=sorted_offers,
            cheapest_flight=min(sorted_offers, key=lambda f: f.price) if sorted_offers else None,
            fastest_flight=min(sorted_offers, key=lambda f: f.duration_minutes) if sorted_offers else None,
            is_live=False,
            source="DEMO DATA (Configure AMADEUS_CLIENT_ID & AMADEUS_CLIENT_SECRET or DUFFEL_API_KEY in .env for live API search)",
            retrieved_at=now_iso,
            provider_name="DemoProvider",
            warning="API credentials not configured in .env. Showing realistic sample data clearly tagged as DEMO DATA."
        )


def sort_flight_offers(offers: List[FlightOffer], sort_by: str = "cheapest") -> List[FlightOffer]:
    """Sort flight offers by cheapest price, shortest duration, or fewest stops."""
    key = (sort_by or "cheapest").lower()
    if key in ["fastest", "duration", "shortest"]:
        return sorted(offers, key=lambda f: (f.duration_minutes, f.price))
    elif key in ["stops", "fewest_stops", "direct"]:
        return sorted(offers, key=lambda f: (f.stops, f.price, f.duration_minutes))
    else:  # cheapest / price
        return sorted(offers, key=lambda f: (f.price, f.duration_minutes, f.stops))


def get_flight_provider() -> BaseFlightProvider:
    """
    Factory function to instantiate the appropriate provider based on environment variables.
    Checks Amadeus credentials first, then Duffel, then falls back to DemoFlightProvider.
    """
    amadeus_client_id = os.getenv("AMADEUS_CLIENT_ID")
    amadeus_client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
    is_prod = os.getenv("AMADEUS_ENV", "test").lower() == "production"

    if amadeus_client_id and amadeus_client_secret and amadeus_client_id != "your_amadeus_client_id_here":
        return AmadeusFlightProvider(amadeus_client_id, amadeus_client_secret, is_production=is_prod)

    duffel_key = os.getenv("DUFFEL_API_KEY")
    if duffel_key and duffel_key != "your_duffel_api_key_here":
        return DuffelFlightProvider(duffel_key)

    return DemoFlightProvider()
