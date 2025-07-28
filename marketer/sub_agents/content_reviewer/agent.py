from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from .prompt import CONTENT_REVIEWER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="content_reviewer_agent",
        description="A Content Review Agent for quality assurance",
        instruction=CONTENT_REVIEWER_INSTR,
    )


content_reviewer_agent = create_agent()
