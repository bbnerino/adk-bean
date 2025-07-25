from google.adk.agents import Agent
from marketer.sub_agents.persona_builder.prompt import PERSONA_BUILDER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="타겟 고객의 페르소나를 분석하고 구축하는 에이전트",
        name="persona_builder_agent",
        instruction=PERSONA_BUILDER_AGENT_INSTR,
    ) 