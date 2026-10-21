"""FastAPI backend application for AgentOS Flight Search and Multi-Agent Platform."""

import os
import sys
from pathlib import Path

# Add project root to path for module imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from agentos import AgentOS
from agents.calculator_agent import create_calculator_agent
from agents.research_agent import create_research_agent
from agents.flight_agent import create_flight_agent
from services.airport_service import search_airports, lookup_iata, get_airport_info
from services.flight_provider import get_flight_provider, FlightSearchResponse
from backend.schemas import (
    FlightSearchRequest,
    FlightSearchResponseSchema,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    AirportItem
)

app = FastAPI(
    title="AgentOS Flight & Multi-Agent API",
    description="Backend runtime for AgentOS flight search, calculator, and research agents.",
    version="1.0.0"
)

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AgentOS runtime singleton
runtime = AgentOS()

print("[AgentOS] Initializing runtime agents...")
try:
    runtime.register_agent("calculator", create_calculator_agent())
except Exception as e:
    print(f"[AgentOS Warning] Failed to initialize calculator agent: {e}")

try:
    runtime.register_agent("researcher", create_research_agent())
except Exception as e:
    print(f"[AgentOS Warning] Failed to initialize researcher agent: {e}")

try:
    runtime.register_agent("flight_agent", create_flight_agent())
except Exception as e:
    print(f"[AgentOS Warning] Failed to initialize flight agent: {e}")


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint displaying runtime status and provider configuration."""
    provider = get_flight_provider()
    is_live = not (provider.__class__.__name__ == "DemoFlightProvider")
    gemini_key_present = bool(os.getenv("GOOGLE_API_KEY"))

    return HealthResponse(
        status="healthy",
        runtime="AgentOS v1.0",
        provider=provider.__class__.__name__,
        is_live_provider=is_live,
        gemini_configured=gemini_key_present,
        registered_agents=list(runtime.agents.keys())
    )


@app.get("/api/airports/search")
def search_airports_endpoint(q: str = Query("", description="Airport code or city query")):
    """Autocomplete airport and city names with IATA codes."""
    return search_airports(q, limit=12)


@app.post("/api/flights/search", response_model=FlightSearchResponseSchema)
def search_flights_endpoint(req: FlightSearchRequest):
    """
    Search for flight offers using the configured flight provider (Amadeus, Duffel, or Demo).
    Returns validated flight offers, schedules, duration, stops, and pricing.
    """
    try:
        provider = get_flight_provider()
        response: FlightSearchResponse = provider.search(
            origin=req.origin,
            destination=req.destination,
            departure_date=req.departure_date,
            return_date=req.return_date,
            adults=req.adults,
            travel_class=req.travel_class,
            direct_only=req.direct_only,
            sort_by=req.sort_by
        )
        return response.to_dict()

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Flight search failed: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """
    Process natural-language requests using AgentOS intelligent routing.
    Routes to flight_agent, calculator, or researcher agent.
    """
    try:
        user_msg = req.message.strip()
        if not user_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Message cannot be empty.")

        target_agent = req.agent if (req.agent and req.agent in runtime.agents) else runtime.route(user_msg)
        agent_response = runtime.run(target_agent, user_msg)

        # If it was a flight query, let's also attempt to extract structured flight data if any
        flight_data = None
        if target_agent == "flight_agent":
            # If the user mentioned flight search terms, run a quick structured search if origin/dest can be inferred
            try:
                # We can check if any search was performed or provide quick structured data
                pass
            except Exception:
                pass

        return ChatResponse(
            agent=target_agent,
            response=agent_response,
            flight_data=flight_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
