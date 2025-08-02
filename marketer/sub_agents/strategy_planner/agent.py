from google.adk.agents import Agent
from marketer.utils.mcp.calculate import calculate_mcp
from .prompt import STRATEGY_PLANNER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="strategy_planner_agent",
        description="A Strategy Planning Agent for marketing campaigns",
        instruction=STRATEGY_PLANNER_INSTR,
        tools=[calculate_mcp],
    )


strategy_planner_agent = create_agent()
