from agentos import AgentOS
from agents.calculator_agent import create_calculator_agent
from agents.research_agent import create_research_agent


# Create the AgentOS runtime
runtime = AgentOS()

# Create two different agents
calculator = create_calculator_agent()
researcher = create_research_agent()

# Register both agents
runtime.register_agent("calculator", calculator)
runtime.register_agent("researcher", researcher)

# Run a calculator task
result1 = runtime.run(
    "calculator",
    "What is 25 multiplied by 8?"
)
print("\nCalculator result:", result1)

# Run a research task
result2 = runtime.run(
    "researcher",
    "Explain what an AI agent is in three sentences."
)
print("\nResearch result:", result2)

# Display task statuses
print("\nTask statuses:", runtime.task_status)