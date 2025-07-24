from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.content_writer.prompt import CONTENT_WRITER_AGENT_INSTR

content_writer_agent = Agent(
    model="gemini-2.5-flash",
    description="다양한 채널의 마케팅 콘텐츠 작성을 담당하는 콘텐츠 작가 에이전트",
    name="content_writer_agent",
    instruction=CONTENT_WRITER_AGENT_INSTR,
    generate_content_config=GenerateContentConfig(temperature=0.3, top_p=0.7),
) 