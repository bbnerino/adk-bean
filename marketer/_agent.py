from google.adk.agents import Agent

import marketer.sub_agents.content_reviewer._agent as content_reviewer
import marketer.sub_agents.persona_builder._agent as persona_builder
import marketer.sub_agents.content_writer._agent as content_writer
import marketer.sub_agents.seo_optimizer._agent as seo_optimizer
import marketer.sub_agents.data_analyst._agent as data_analyst
import marketer.sub_agents.trend_researcher._agent as trend_researcher
import marketer.sub_agents.strategy_planner._agent as strategy_planner
from marketer.prompt import ROOT_AGENT_INSTR


def create_marketer_agent(instruction: str = None, tools: list = []):
    if instruction is None:
        instruction = ROOT_AGENT_INSTR
    else:
        instruction = ROOT_AGENT_INSTR + "\n" + instruction

    return Agent(
        model="gemini-2.5-flash",
        name="marketer_agent",
        description="A Marketing AI using the services of multiple sub-agents",
        instruction=instruction,
        sub_agents=[
            content_reviewer.create_agent(),
            persona_builder.create_agent(),
            content_writer.create_agent(),
            seo_optimizer.create_agent(),
            data_analyst.create_agent(),
            trend_researcher.create_agent(),
            strategy_planner.create_agent(),
        ],
        tools=tools,
    )
