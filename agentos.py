"""AgentOS Runtime: Core platform for autonomous multi-agent execution and routing."""

from typing import Dict, Any, Optional, Tuple
import re


def _clean_content(content: Any) -> str:
    """Normalize LangChain message content to a clean string."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


class AgentOS:
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.task_status: Dict[int, str] = {}

    def register_agent(self, name: str, agent: Any):
        """Register an agent with AgentOS."""
        self.agents[name] = agent
        print(f"Agent registered: {name}")

    def run(self, agent_name: str, task: str) -> str:
        """Execute a task using a registered agent."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")

        task_id = len(self.task_status) + 1
        self.task_status[task_id] = "RUNNING"

        try:
            agent = self.agents[agent_name]

            result = agent.invoke({
                "messages": [
                    {"role": "user", "content": task}
                ]
            })

            self.task_status[task_id] = "COMPLETED"
            raw_content = result["messages"][-1].content
            return _clean_content(raw_content)

        except Exception:
            self.task_status[task_id] = "FAILED"
            raise

    def route(self, task: str) -> str:
        """
        Intelligently route a natural-language task to the appropriate registered agent:
        'flight_agent' (or 'flights'), 'calculator', or 'researcher'.
        """
        lower_task = task.lower().strip()

        # Flight search keywords
        flight_keywords = [
            "flight", "flights", "fly", "flying", "airline", "airlines", "airport", "airports",
            "ticket", "tickets", "airfare", "fares", "departure", "arrival", "layover",
            "non-stop", "direct flight", "round-trip", "one-way", "round trip", "one way",
            "iata", "boarding", "terminal", "book flight", "plane"
        ]
        if any(re.search(rf"\b{re.escape(k)}\b", lower_task) for k in flight_keywords):
            if "flight_agent" in self.agents:
                return "flight_agent"
            if "flights" in self.agents:
                return "flights"

        # Math / calculation keywords
        calc_keywords = [
            "multiply", "multiplied", "product of", "divide", "divided", "sum of",
            "calculate", "calculator", "add", "subtract", "plus", "minus", "times"
        ]
        has_math_ops = bool(re.search(r"\b\d+\s*[\*\+\-\/\^]\s*\d+\b", lower_task))
        if has_math_ops or any(re.search(rf"\b{re.escape(k)}\b", lower_task) for k in calc_keywords):
            if "calculator" in self.agents:
                return "calculator"

        # Default fallback to researcher (or first registered agent)
        if "researcher" in self.agents:
            return "researcher"

        return list(self.agents.keys())[0] if self.agents else "researcher"

    def route_and_run(self, task: str) -> Tuple[str, str]:
        """Automatically route the task and execute it with the selected agent."""
        target_agent = self.route(task)
        result = self.run(target_agent, task)
        return target_agent, result