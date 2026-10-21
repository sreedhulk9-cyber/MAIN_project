"""Flight Search Agent integrated with AgentOS and Gemini.
Interprets natural language queries, resolves airports, calls flight search tools,
and presents verified flight details.
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any
import json

from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

from services.airport_service import lookup_iata, search_airports, get_airport_info
from services.flight_provider import get_flight_provider, FlightSearchResponse


def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    travel_class: str = "ECONOMY",
    direct_only: bool = False,
    sort_by: str = "cheapest"
) -> str:
    """
    Search for flights between origin and destination cities/airports.

    Parameters:
    - origin: Origin city name or 3-letter IATA code (e.g. 'Kochi', 'COK', 'Delhi', 'DEL')
    - destination: Destination city name or 3-letter IATA code (e.g. 'Bangalore', 'BLR', 'Dubai', 'DXB')
    - departure_date: Departure date in YYYY-MM-DD format
    - return_date: Optional return date in YYYY-MM-DD format for round trips
    - adults: Number of adult passengers (default 1)
    - travel_class: 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', or 'FIRST'
    - direct_only: True to filter only direct / non-stop flights
    - sort_by: 'cheapest', 'fastest', or 'fewest_stops'
    """
    try:
        provider = get_flight_provider()
        response: FlightSearchResponse = provider.search(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=adults,
            travel_class=travel_class,
            direct_only=direct_only,
            sort_by=sort_by
        )

        res_dict = response.to_dict()
        return json.dumps(res_dict, indent=2)

    except ValueError as ve:
        return json.dumps({
            "error": "Validation Error",
            "message": str(ve),
            "flights": []
        })
    except Exception as e:
        return json.dumps({
            "error": "Provider Error",
            "message": f"Flight search failed: {str(e)}",
            "flights": []
        })


def lookup_airport_code(query: str) -> str:
    """
    Lookup airport information and 3-letter IATA code for any city or airport name.
    Useful when confirming airport codes for cities like Kochi (COK), Delhi (DEL), Bangalore (BLR), Dubai (DXB).
    """
    try:
        iata = lookup_iata(query)
        if not iata:
            candidates = search_airports(query, limit=5)
            return json.dumps({"found": False, "query": query, "candidates": candidates})

        info = get_airport_info(iata)
        return json.dumps({"found": True, "query": query, "airport": info})
    except Exception as e:
        return json.dumps({"error": str(e)})


def create_flight_agent():
    """Create and return a LangChain flight agent powered by Gemini."""
    today_str = date.today().isoformat()
    tomorrow_str = (date.today() + timedelta(days=1)).isoformat()

    system_prompt = f"""You are the AgentOS Flight Search Agent, a specialized flight assistant.
Current Date: {today_str} (Tomorrow: {tomorrow_str}).

Your duties:
1. Parse natural-language user requests to extract:
   - Origin airport/city
   - Destination airport/city
   - Departure date (convert relative dates like 'tomorrow', 'next Monday', or '15 November 2026' to YYYY-MM-DD)
   - Return date (for round-trips)
   - Passenger count (default 1)
   - Cabin class (ECONOMY, BUSINESS, etc.)
   - Direct-flight preference
2. If ANY essential information is missing (Origin, Destination, or Departure Date), do NOT search or guess. Instead, politely ask the user a clear follow-up question.
3. NEVER fabricate flight schedules, prices, airline names, or booking links. All flight information MUST come strictly from invoking the `search_flights` tool.
4. When `search_flights` returns results:
   - Clearly state the route, date, and passenger count.
   - Present the available flight offers cleanly with:
     * Airline & Flight Number
     * Departure time & Arrival time
     * Duration & number of stops (and layover cities if any)
     * Total Fare & Currency
   - Clearly highlight the CHEAPEST option and FASTEST option.
   - Mention the Data Source and Retrieval Timestamp provided in the tool output.
   - If the tool indicates DEMO DATA (due to unconfigured live credentials), explicitly inform the user that results are demo sample data and live Amadeus/Duffel credentials can be configured in .env.
"""

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash"
    )

    agent = create_agent(
        model=model,
        tools=[search_flights, lookup_airport_code],
        system_prompt=system_prompt
    )

    return agent
