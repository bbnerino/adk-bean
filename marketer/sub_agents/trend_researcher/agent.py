from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from .prompt import TREND_RESEARCHER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="trend_researcher_agent",
        description="A Trend Research Agent for market analysis",
        instruction=TREND_RESEARCHER_INSTR,
    )


trend_researcher_agent = create_agent()
