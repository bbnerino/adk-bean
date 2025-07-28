from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.data_analyst.prompt import DATA_ANALYST_AGENT_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="마케팅 성과 분석 및 데이터 기반 인사이트 도출을 담당하는 분석·리포트 에이전트",
        name="data_analyst_agent",
        instruction=DATA_ANALYST_AGENT_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    )


data_analyst_agent = create_agent()
