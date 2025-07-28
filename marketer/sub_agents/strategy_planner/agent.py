from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.genai.types import GenerateContentConfig
from marketer.sub_agents.strategy_planner.prompt import STRATEGY_PLANNER_AGENT_INSTR


def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        description="마케팅 전략 수립 및 캠페인 기획을 담당하는 전략 기획 에이전트",
        name="strategy_planner_agent",
        instruction=STRATEGY_PLANNER_AGENT_INSTR,
        generate_content_config=GenerateContentConfig(temperature=0.1, top_p=0.5),
    )


strategy_planner_agent = create_agent()
