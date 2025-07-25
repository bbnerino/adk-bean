from google.adk.agents import Agent
from marketer.sub_agents.seo_optimizer.prompt import SEO_OPTIMIZER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="SEO 최적화 전략을 제시하는 에이전트",
        name="seo_optimizer_agent",
        instruction=SEO_OPTIMIZER_AGENT_INSTR,
    ) 