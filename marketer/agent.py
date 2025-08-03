from google.adk.agents import Agent

from marketer.sub_agents.content_reviewer.agent import content_reviewer_agent
from marketer.sub_agents.content_writer.agent import content_writer_agent
from marketer.sub_agents.seo_optimizer.agent import seo_optimizer_agent
from marketer.sub_agents.strategy_planner.agent import strategy_planner_agent
from marketer.prompt import ROOT_AGENT_INSTR
from google.adk.tools.agent_tool import AgentTool

from marketer.utils.mcp.load_web_tool import load_web_tool
from marketer.utils.mcp.payment_agent import payment_agent_tool

root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="A Marketing AI using the services of multiple sub-agents",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[
        content_reviewer_agent,
        content_writer_agent,
        seo_optimizer_agent,
        strategy_planner_agent,
    ],
    tools=[
        load_web_tool,
        payment_agent_tool
    ],
)
