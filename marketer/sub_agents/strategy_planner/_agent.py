from google.adk.agents import Agent
from marketer.sub_agents.strategy_planner.prompt import STRATEGY_PLANNER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="마케팅 전략을 수립하는 에이전트",
        name="strategy_planner_agent",
        instruction=STRATEGY_PLANNER_AGENT_INSTR,
    ) 