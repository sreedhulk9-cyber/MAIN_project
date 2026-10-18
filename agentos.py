class AgentOS:
    def __init__(self):
        self.agents = {}
        self.task_status = {}

    def register_agent(self, name, agent):
        """Register an agent with AgentOS."""
        self.agents[name] = agent
        print(f"Agent registered: {name}")

    def run(self, agent_name, task):
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
            return result["messages"][-1].content

        except Exception:
            self.task_status[task_id] = "FAILED"
            raise