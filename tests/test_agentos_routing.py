import pytest
from agentos import AgentOS


def test_agentos_routing_rules():
    runtime = AgentOS()
    runtime.register_agent("calculator", object())
    runtime.register_agent("researcher", object())
    runtime.register_agent("flight_agent", object())

    # Flight queries
    assert runtime.route("Find flights from Kochi to Delhi tomorrow") == "flight_agent"
    assert runtime.route("Find the cheapest flight from Kochi to Bangalore on 15 November 2026") == "flight_agent"
    assert runtime.route("Compare flights from Kochi to Mumbai for two adults") == "flight_agent"
    assert runtime.route("Find direct flights from Delhi to Kochi") == "flight_agent"
    assert runtime.route("Find round-trip flights from Kochi to Dubai") == "flight_agent"

    # Math queries
    assert runtime.route("What is 25 multiplied by 8?") == "calculator"
    assert runtime.route("Calculate 100 divided by 4") == "calculator"
    assert runtime.route("What is the sum of 45 and 90?") == "calculator"

    # Research queries
    assert runtime.route("Explain what an AI agent is in three sentences.") == "researcher"
    assert runtime.route("Summarize the history of aviation") == "researcher"


def test_agentos_missing_agent_error():
    runtime = AgentOS()
    with pytest.raises(ValueError, match="Agent not found"):
        runtime.run("non_existent_agent", "Do something")
