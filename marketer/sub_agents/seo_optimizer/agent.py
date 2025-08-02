from google.adk.agents import Agent
from marketer.sub_agents.seo_optimizer.prompt import SEO_OPTIMIZER_INSTR
from marketer.utils.mcp.aeo_agent import aeo_agent

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="seo_optimizer_agent",
        description="SEO 최적화를 수행하는 에이전트",
        instruction=SEO_OPTIMIZER_INSTR,
        tools=[aeo_agent],
    )

seo_optimizer_agent = create_agent()
