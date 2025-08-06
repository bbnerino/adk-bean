from google.adk.agents import Agent


SEARCH_DECISION_INSTR = """
당신은 검색 결정 에이전트입니다.

## 주요 역할
- 사용자의 질문에서 검색 필요성 판단
- 구글 검색 질문 생성
- 결과 분석 및 요약
"""
search_decision_agent = Agent(
    model="gemini-2.5-flash",
    name="search_decision_agent",
    description="A Search Decision Agent for marketing content",
    instruction=SEARCH_DECISION_INSTR,
)
