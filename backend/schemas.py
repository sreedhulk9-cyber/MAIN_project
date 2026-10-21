"""Pydantic schemas for the AgentOS Backend API."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class FlightSearchRequest(BaseModel):
    origin: str = Field(..., description="Origin airport code or city name (e.g. COK or Kochi)")
    destination: str = Field(..., description="Destination airport code or city name (e.g. DEL or Delhi)")
    departure_date: str = Field(..., description="Departure date in YYYY-MM-DD format")
    return_date: Optional[str] = Field(None, description="Optional return date in YYYY-MM-DD format")
    adults: int = Field(1, ge=1, le=9, description="Number of adult passengers")
    travel_class: str = Field("ECONOMY", description="Cabin class: ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST")
    direct_only: bool = Field(False, description="Filter for direct / non-stop flights only")
    sort_by: str = Field("cheapest", description="Sorting criteria: cheapest, fastest, fewest_stops")


class FlightSegmentSchema(BaseModel):
    carrier_code: str
    carrier_name: str
    flight_number: str
    departure_airport: str
    departure_time: str
    arrival_airport: str
    arrival_time: str
    duration: str


class FlightOfferSchema(BaseModel):
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
    stop_airports: List[str] = []
    segments: List[Dict[str, Any]] = []
    price: float
    currency: str
    cabin_class: str
    seats_available: Optional[int] = None
    booking_url: Optional[str] = None
    is_round_trip: bool = False
    return_flight: Optional[Dict[str, Any]] = None
    is_demo: bool = False


class FlightSearchResponseSchema(BaseModel):
    query: Dict[str, Any]
    results_count: int
    flights: List[FlightOfferSchema]
    cheapest_flight: Optional[FlightOfferSchema] = None
    fastest_flight: Optional[FlightOfferSchema] = None
    is_live: bool
    source: str
    retrieved_at: str
    provider_name: str
    warning: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's natural language request")
    agent: Optional[str] = Field(None, description="Explicit agent name (flight_agent, calculator, researcher), or auto-routed if omitted")


class ChatResponse(BaseModel):
    agent: str
    response: str
    flight_data: Optional[FlightSearchResponseSchema] = None


class AirportItem(BaseModel):
    iata: str
    name: str
    city: str
    state: Optional[str] = ""
    country: str


class HealthResponse(BaseModel):
    status: str
    runtime: str
    provider: str
    is_live_provider: bool
    gemini_configured: bool
    registered_agents: List[str]
