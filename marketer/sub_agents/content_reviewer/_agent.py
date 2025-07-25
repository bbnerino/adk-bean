from google.adk.agents import Agent
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.content_reviewer.prompt import CONTENT_REVIEWER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="콘텐츠 품질 검토 및 개선 제안을 담당하는 피드백 평가 에이전트",
        name="content_reviewer_agent",
        instruction=CONTENT_REVIEWER_AGENT_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    ) 