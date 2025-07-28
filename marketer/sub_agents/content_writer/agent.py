from google.adk.agents import Agent
from .prompt import CONTENT_WRITER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="content_writer_agent",
        description="A Content Writing Agent for marketing content",
        instruction=CONTENT_WRITER_INSTR,
    )


content_writer_agent = create_agent()
