from google.adk.agents import Agent
from marketer.sub_agents.content_writer.prompt import CONTENT_WRITER_AGENT_INSTR

def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="마케팅 콘텐츠를 작성하는 에이전트",
        name="content_writer_agent",
        instruction=CONTENT_WRITER_AGENT_INSTR,
    ) 