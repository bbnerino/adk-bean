from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from .prompt import PERSONA_BUILDER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="persona_builder_agent",
        description="A Persona Building Agent for target audience analysis",
        instruction=PERSONA_BUILDER_INSTR,
    )


persona_builder_agent = create_agent()
