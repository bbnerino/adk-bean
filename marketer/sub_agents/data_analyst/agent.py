from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from .prompt import DATA_ANALYST_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="data_analyst",
        description="A Data Analysis Agent for marketing insights",
        instruction=DATA_ANALYST_INSTR,
    )


data_analyst_agent = create_agent()
