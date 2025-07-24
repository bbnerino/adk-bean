from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.persona_builder.prompt import PERSONA_BUILDER_AGENT_INSTR

persona_builder_agent = Agent(
    model="gemini-2.5-flash",
    description="타겟 고객 페르소나 설계 및 고객 여정 맵 작성을 담당하는 고객 페르소나 설계 에이전트",
    name="persona_builder_agent",
    instruction=PERSONA_BUILDER_AGENT_INSTR,
    generate_content_config=GenerateContentConfig(temperature=0.2, top_p=0.6),
) 