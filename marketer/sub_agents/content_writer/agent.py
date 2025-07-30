from google.adk.agents import Agent

from marketer.utils.tools.patch_content import patch_content
from marketer.utils.tools.update_content import update_content
from .prompt import CONTENT_WRITER_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="content_writer_agent",
        description="A Content Writing Agent for marketing content",
        instruction=CONTENT_WRITER_INSTR,
        tools=[update_content, patch_content],
    )


content_writer_agent = create_agent()
