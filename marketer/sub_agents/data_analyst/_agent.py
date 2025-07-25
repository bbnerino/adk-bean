from google.adk.agents import Agent
from marketer.sub_agents.data_analyst.prompt import DATA_ANALYST_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="데이터 분석을 수행하는 에이전트",
        name="data_analyst_agent",
        instruction=DATA_ANALYST_AGENT_INSTR,
    ) 