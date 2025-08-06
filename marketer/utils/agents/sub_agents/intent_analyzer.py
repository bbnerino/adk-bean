from google.adk.agents import Agent


INTENT_ANALYZER_INSTR = """
당신은 의도 분석 에이전트입니다.

## 주요 역할
- 사용자의 질문에서 핵심 키워드와 리서치 목적을 분석

"""


intent_analyzer_agent = Agent(
    model="gemini-2.5-flash",
    name="intent_analyzer_agent",
    description="A Intent Analyzer Agent for marketing content",
    instruction=INTENT_ANALYZER_INSTR,
)
