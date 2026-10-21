from dotenv import load_dotenv

load_dotenv()

from agentos import AgentOS
from agents.calculator_agent import create_calculator_agent
from agents.research_agent import create_research_agent
from agents.flight_agent import create_flight_agent


# Create the AgentOS runtime
runtime = AgentOS()

# Create agents
calculator = create_calculator_agent()
researcher = create_research_agent()
flight_agent = create_flight_agent()

# Register all agents in AgentOS
runtime.register_agent("calculator", calculator)
runtime.register_agent("researcher", researcher)
runtime.register_agent("flight_agent", flight_agent)

# 1. Run a calculator task
result1 = runtime.run(
    "calculator",
    "What is 25 multiplied by 8?"
)
print("\nCalculator result:", result1)

# 2. Run a research task
result2 = runtime.run(
    "researcher",
    "Explain what an AI agent is in three sentences."
)
print("\nResearch result:", result2)

# 3. Demonstrate intelligent routing
routed_agent, result3 = runtime.route_and_run("Find the cheapest flight from Kochi to Bangalore on 15 November 2026")
print(f"\n[Routed to '{routed_agent}'] Flight Search Result:\n", result3)

# Display final task statuses
print("\nTask statuses:", runtime.task_status)