"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""

from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent

from google_tools.utils.tools.google_trend_tool import google_trend_tool


SEARCH_DECISION_INSTR = """
당신은 검색 결정 에이전트입니다.

## 주요 역할
- 사용자의 질문에서 검색 필요성 판단
- 구글 검색 질문 생성
- 결과 분석 및 요약

## 사용 도구
- tools: google_trend_tool

"""
google_trend_agent = Agent(
    model="gemini-2.5-flash",
    name="google_trend_agent",
    description="A Search Decision Agent for marketing content",
    instruction=SEARCH_DECISION_INSTR,
    tools=[google_trend_tool],
)
