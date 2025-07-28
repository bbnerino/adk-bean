from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.seo_optimizer.prompt import SEO_OPTIMIZER_AGENT_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="검색엔진 최적화 및 키워드 전략을 담당하는 SEO 최적화 에이전트",
        name="seo_optimizer_agent",
        instruction=SEO_OPTIMIZER_AGENT_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    )


seo_optimizer_agent = create_agent()
