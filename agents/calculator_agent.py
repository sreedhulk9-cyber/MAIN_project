from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    print("Calculator tool called!")
    return a * b


def create_calculator_agent():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash"
    )

    agent = create_agent(
        model=model,
        tools=[multiply]
    )

    return agent