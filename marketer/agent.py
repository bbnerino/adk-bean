from google.adk.agents import Agent

from marketer.sub_agents.content_reviewer.agent import content_reviewer_agent
from marketer.sub_agents.persona_builder.agent import persona_builder_agent
from marketer.sub_agents.content_writer.agent import content_writer_agent
from marketer.sub_agents.seo_optimizer.agent import seo_optimizer_agent
from marketer.sub_agents.data_analyst.agent import data_analyst_agent
from marketer.sub_agents.trend_researcher.agent import trend_researcher_agent
from marketer.sub_agents.strategy_planner.agent import strategy_planner_agent
from marketer.prompt import ROOT_AGENT_INSTR

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A Marketing AI using the services of multiple sub-agents",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[
        content_reviewer_agent,
        persona_builder_agent,
        content_writer_agent,
        seo_optimizer_agent,
        data_analyst_agent,
        trend_researcher_agent,
        strategy_planner_agent,
    ],
)
