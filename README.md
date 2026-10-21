# AgentOS — Autonomous Multi-Agent Flight Search Platform

AgentOS is a runtime platform for autonomous multi-agent AI systems, built with **Python**, **LangChain**, **Google Gemini**, **FastAPI**, and a **React (Vite)** frontend.

It provides autonomous coordination across multiple specialized agents:
- 🛫 **Flight Search Agent (`flight_agent`)**: Extracts travel parameters from natural-language requests, maps city names to 3-letter IATA codes, searches live flight data via Amadeus or Duffel APIs, sorts results by price/duration/stops, and presents verified offers without fabrication.
- 🧮 **Calculator Agent (`calculator`)**: Evaluates arithmetic expressions and math operations using tool calling.
- 🔬 **Researcher Agent (`researcher`)**: Synthesizes explanations, research summaries, and domain concepts.
- 🧭 **Intelligent Router**: Intelligently classifies natural-language user queries and dynamically delegates them to the most suitable agent.

---

## Architecture & Agent Workflow

```
                        [ User / Web UI / CLI ]
                                   │
                                   ▼
                       [ AgentOS Router & API ]
                      (backend/main.py & agentos.py)
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        ▼                          ▼                          ▼
 [ Calculator Agent ]     [ Researcher Agent ]     [ Flight Search Agent ]
(agents/calculator_agent) (agents/research_agent)  (agents/flight_agent)
        │                          │                          │
        ▼                          ▼                          ▼
  multiply tool              Gemini 3.8-Flash          search_flights tool
                                                    lookup_airport_code tool
                                                              │
                                                              ▼
                                                   [ Flight Provider Engine ]
                                                  (services/flight_provider)
                                                              │
                                       ┌──────────────────────┴──────────────────────┐
                                       ▼                                             ▼
                               [ Amadeus API ]                              [ Transparent Demo ]
                          (OAuth2 Client Credentials)                      (Tagged clearly when
                                                                            keys unconfigured)
```

---

## Project Structure

```
agentos_project/
  agents/
    calculator_agent.py   # Multi-agent math tool execution
    research_agent.py     # Gemini research synthesis
    flight_agent.py       # Natural-language flight parsing & tool coordinator
  services/
    flight_provider.py    # Modular flight provider (Amadeus, Duffel, Demo fallback)
    airport_service.py    # Global airport & city IATA lookup and autocomplete
  backend/
    main.py               # FastAPI backend with CORS, /api/flights/search, /api/chat, /api/health
    schemas.py            # Pydantic request & response validation schemas
  frontend/
    src/
      components/
        Navbar.jsx        # AgentOS branding, tabs, and provider health badge
        SearchForm.jsx    # Airport autocomplete, date pickers, class & direct filter
        FlightCard.jsx    # Flight details, departure/arrival times, stops, fares
        FlightList.jsx    # Results sorting (cheapest/fastest/stops) and live timestamp
        ChatBox.jsx       # Conversational AI assistant with multi-agent routing
        HealthModal.jsx   # Credentials setup guide and runtime health dialog
      services/
        api.js            # Frontend REST client
      App.jsx             # Main container
      index.css           # Premium vanilla CSS design system
    package.json
  tests/
    test_airport_service.py
    test_flight_provider.py
    test_agentos_routing.py
    test_api.py
  agentos.py              # AgentOS runtime kernel with routing & task management
  main.py                 # CLI demonstration running all registered agents
  .env                    # Secrets and environment variables (excluded from Git)
  .env.example            # Placeholder environment template
  .gitignore
  requirements.txt        # Python backend dependencies
  README.md
```

---

## Prerequisites

- **Python 3.10+** (Tested on Python 3.13)
- **Node.js 18+** and **npm**
- **Google Gemini API Key** (Required for LangChain Gemini reasoning)

---

## Environment Configuration

1. Create or verify your `.env` file in the root directory:
   ```bash
   copy .env.example .env
   ```

2. Open `.env` and set your API keys:
   ```env
   # Required for Gemini reasoning
   GOOGLE_API_KEY=your_gemini_api_key_here

   # Optional for Live Flight Offers (Amadeus Self-Service)
   AMADEUS_CLIENT_ID=your_amadeus_api_key_here
   AMADEUS_CLIENT_SECRET=your_amadeus_api_secret_here
   AMADEUS_ENV=test
   ```

### Obtaining Free Amadeus API Credentials
1. Register for a free developer account at [Amadeus for Developers](https://developers.amadeus.com/).
2. Navigate to **My Self-Service Workspace** > **Create New App**.
3. Copy your **API Key** (Client ID) and **API Secret** into `.env`.
4. The test environment includes 2,000 free monthly flight offer searches.
5. If credentials are not provided, AgentOS automatically activates **Demo Mode**, clearly tagging all sample data as `DEMO DATA` in accordance with platform transparency rules.

---

## Windows Launch Commands

Open two separate terminals (PowerShell or Command Prompt):

### Terminal 1: Backend (FastAPI)
```powershell
# Navigate to project root
cd c:\Users\HP\Desktop\AgentOS\agentos_project

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install backend dependencies (if needed)
pip install -r requirements.txt

# Launch FastAPI backend on port 8000
python -m uvicorn backend.main:app --reload --port 8000
```
Backend API will be running at: `http://127.0.0.1:8000` (API Docs at `http://127.0.0.1:8000/docs`).

### Terminal 2: Frontend (Vite + React)
```powershell
# Navigate to frontend folder
cd c:\Users\HP\Desktop\AgentOS\agentos_project\frontend

# Install dependencies (first time only)
npm install

# Launch frontend dev server
npm run dev
```
Web interface will be running at: `http://localhost:5173`.

---

## Running Automated Tests

Run the full pytest test suite from the project root:
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

This validates:
- Airport and IATA code resolution (Kochi -> `COK`, Delhi -> `DEL`, Bangalore -> `BLR`, Dubai -> `DXB`).
- Search parameter validation (rejects past dates, same origin/destination, invalid dates).
- Flight provider offer generation, currency calculation, and sorting algorithms.
- AgentOS task registration and intelligent query routing.
- FastAPI endpoints (`/api/health`, `/api/airports/search`, `/api/flights/search`).

---

## CLI Demonstration

To test the multi-agent system directly via terminal:
```powershell
.\.venv\Scripts\python.exe main.py
```
This runs:
1. Calculator agent: `What is 25 multiplied by 8?`
2. Researcher agent: `Explain what an AI agent is in three sentences.`
3. Flight agent: `Find the cheapest flight from Kochi to Bangalore on 15 November 2026.`

---

## Sample Natural-Language Flight Requests

Try typing these in the **AI Agent Chat** box or via the API:
- *"Find flights from Kochi to Delhi tomorrow."*
- *"Find the cheapest flight from Kochi to Bangalore on 15 November 2026."*
- *"Compare flights from Kochi to Mumbai for two adults."*
- *"Find direct flights from Delhi to Kochi."*
- *"Find round-trip flights from Kochi to Dubai, departing on 15 November and returning on 22 November 2026."*
- *"What is 25 multiplied by 8?"* (automatically routed to Calculator)
- *"Explain what an AI agent is in three sentences."* (automatically routed to Researcher)

### Verifying Provider Response Source
In both the web UI and API responses:
- Each flight search response contains `source`, `is_live`, and `retrieved_at`.
- When live credentials are set, the UI displays `Source: Amadeus Flight Offers API (Test/Live Environment)` with exact ISO retrieval timestamps.
- When live credentials are not present, results are explicitly marked with a yellow `DEMO DATA` badge and warning text so simulated flights are never mistaken for real bookings.
