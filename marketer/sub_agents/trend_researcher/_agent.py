from google.adk.agents import Agent
from marketer.sub_agents.trend_researcher.prompt import TREND_RESEARCHER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="시장 트렌드를 분석하는 에이전트",
        name="trend_researcher_agent",
        instruction=TREND_RESEARCHER_AGENT_INSTR,
    ) 