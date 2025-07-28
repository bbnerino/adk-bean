from google.adk.agents import Agent
from .prompt import SEO_OPTIMIZER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="seo_optimizer_agent",
        description="An SEO Optimization Agent for content optimization",
        instruction=SEO_OPTIMIZER_INSTR,
    )


seo_optimizer_agent = create_agent()
