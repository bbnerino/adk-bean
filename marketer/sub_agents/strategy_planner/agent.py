from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from .prompt import STRATEGY_PLANNER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="strategy_planner",
        description="A Strategy Planning Agent for marketing campaigns",
        instruction=STRATEGY_PLANNER_INSTR,
    )


strategy_planner_agent = create_agent()
