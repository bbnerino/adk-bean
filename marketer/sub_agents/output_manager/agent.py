from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.prompt import OUTPUT_MANAGER_INSTR


def create_agent():
    return Agent(
        model="gemini-1.5-flash",
        description="콘텐츠 결과물 관리 에이전트",
        name="output_manager_agent",
        instruction=OUTPUT_MANAGER_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    )


output_manager_agent = create_agent()
