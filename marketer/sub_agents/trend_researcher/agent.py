from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.trend_researcher.prompt import TREND_RESEARCHER_AGENT_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="시장 트렌드 분석 및 경쟁사 조사를 담당하는 트렌드 리서처 에이전트",
        name="trend_researcher_agent",
        instruction=TREND_RESEARCHER_AGENT_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    )


trend_researcher_agent = create_agent()
