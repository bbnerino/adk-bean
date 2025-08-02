from google.adk.agents import Agent

import marketer.sub_agents.content_reviewer.agent as content_reviewer
import marketer.sub_agents.content_writer.agent as content_writer
import marketer.sub_agents.seo_optimizer.agent as seo_optimizer
import marketer.sub_agents.strategy_planner.agent as strategy_planner
from marketer.prompt import ROOT_AGENT_INSTR
from marketer.utils.mcp.calculate import calculate_mcp
from marketer.utils.tools.patch_content import patch_content
from marketer.utils.tools.update_content import update_content

# from marketer.utils.mcp.file_system import file_system_mcp


def create_marketer_agent(instruction: str = None):
    tools = [
        update_content,
        patch_content,
        calculate_mcp,
    ]
    tools_str = "\n".join([tool.name for tool in tools])
    if instruction is None:
        instruction = (
            ROOT_AGENT_INSTR
            + f"\n You can use the following tools to help you: {tools_str}"
        )
    else:
        instruction = (
            ROOT_AGENT_INSTR
            + "\n"
            + instruction
            + f"\n You can use the following tools to help you: {tools_str}"
        )

    return Agent(
        model="gemini-2.5-flash",
        name="marketer_agent",
        description="A Marketing AI using the services of multiple sub-agents",
        instruction=instruction,
        sub_agents=[
            content_writer.create_agent(),
            content_reviewer.create_agent(),
            seo_optimizer.create_agent(),
            strategy_planner.create_agent(),
        ],
        tools=tools,
    )
