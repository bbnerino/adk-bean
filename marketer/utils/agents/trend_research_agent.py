from google.adk.agents import Agent, LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.tool_context import ToolContext

from google.adk.tools import google_search

from marketer.sub_agents.intent_analyzer.agent import intent_analyzer_agent
from marketer.sub_agents.search_decision_agent.agent import search_decision_agent


TREND_RESEARCH_AGENT_INSTR = """
당신은 트렌드 리서치 코디네이터입니다.

## 필수 작업 순서 (반드시 따라야 함)

### ⚠️ 중요: 절대로 직접 분석하지 마세요!
모든 작업은 반드시 해당 전문 에이전트에게 위임해야 합니다.

### STEP 1: 질문 의도 분석 (필수)
- 반드시 `transfer_to_agent`를 사용해서 `intent_analyzer_agent`에게 질문 분석을 요청하세요
- 직접 키워드를 분석하지 마세요

### STEP 2: 검색 필요성 판단 (필수)  
- 반드시 `transfer_to_agent`를 사용해서 `search_decision_agent`에게 검색 필요성 판단을 요청하세요
- 직접 검색 필요성을 판단하지 마세요

### STEP 3: 검색 실행 (조건부)
- search_decision_agent가 검색이 필요하다고 판단한 경우에만 `google_search_grounding` 도구를 사용하세요

### STEP 4: 결과 종합 및 요약
- 모든 sub_agents의 결과를 받은 후에만 최종 답변을 제공하세요

## 작업 규칙
1. 첫 번째 응답에서는 반드시 `intent_analyzer_agent`로 transfer하세요
2. 각 단계를 순차적으로 진행하세요
3. Sub_agents의 작업 결과를 기다린 후 다음 단계로 진행하세요
4. 최종 단계에서만 종합적인 분석을 제공하세요

## 금지사항
- 직접 질문을 분석하는 것
- 직접 검색 필요성을 판단하는 것  
- Sub_agents를 건너뛰고 바로 검색하는 것
- 중간 과정을 생략하는 것
"""


async def trend_research_agent_tool(
    question: str,
    tool_context: ToolContext,
):
    """Tool to call trend research agent with mandatory sub-agent workflow."""

    agent_tool = AgentTool(
        agent=Agent(
            model="gemini-2.5-flash",
            name="trend_research_agent",
            description="트렌드 분석 및 최신 정보 리서치를 담당하는 전문 에이전트 (Sub-agents 필수 사용)",
            instruction=TREND_RESEARCH_AGENT_INSTR,
            sub_agents=[
                intent_analyzer_agent,
                search_decision_agent,
            ],
            tools=[google_search_grounding],
        )
    )

    trend_research_agent_output = await agent_tool.run_async(
        args={"request": question}, tool_context=tool_context
    )

    return trend_research_agent_output


google_search_grounding = AgentTool(
    agent=Agent(
        model="gemini-2.5-flash",
        name="google_search_grounding",
        description="An agent providing Google-search grounding capability",
        instruction=""",
    Answer the user's question directly using google_search grounding tool; Provide a brief but concise response. 
    Rather than a detail response, provide the immediate actionable item for a tourist or traveler, in a single sentence.
    Do not ask the user to check or look up information for themselves, that's role; do your best to be informative.
    """,
        tools=[google_search],
    )
)
