from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI


def create_research_agent():
    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash"
    )

    agent = create_agent(
        model=model,
        tools=[]
    )

    return agent