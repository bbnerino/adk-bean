"""
Weather LLM Agent MCP Server
LLM 기반 날씨 분석 에이전트를 MCP 서버로 구현
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK Imports
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from weather_tools import WeatherTool, ForecastTool

# Load environment variables
load_dotenv()

# Weather LLM Agent Instruction
WEATHER_AGENT_INSTR = """
당신은 날씨 전문 분석 에이전트입니다.

## 주요 역할
- 날씨 정보를 수집하고 분석
- 날씨 패턴과 트렌드 해석
- 마케팅/비즈니스 관점에서 날씨의 영향 분석
- 날씨 기반 추천사항 제공

## 사용 가능한 도구
- get_weather: 특정 도시의 현재 날씨 정보 조회
- get_forecast: 특정 도시의 일기예보 정보 조회

## 응답 스타일
1. 먼저 관련 날씨 데이터를 수집
2. 데이터를 분석하고 패턴 파악
3. 마케팅/비즈니스 관점의 실용적 인사이트 제공
4. 구체적이고 실행 가능한 추천사항 제시

## 예시
사용자: "서울 날씨 어때?"
응답: 
1. 서울 현재 날씨 조회
2. "현재 서울은 맑은 날씨로 기온이 25°C입니다. 
3. 이런 좋은 날씨는 야외 활동 관련 마케팅에 최적입니다.
4. 카페 테라스, 공원 피크닉 용품, 선글라스 등의 광고 효과가 높을 것으로 예상됩니다."

항상 데이터 기반으로 분석하고, 실용적인 조언을 제공하세요.
"""


class WeatherLLMAgentTool:
    """Weather LLM Agent를 래핑한 클래스"""

    def __init__(self):
        print("Initializing Weather LLM Agent...")

        # Weather LLM Agent 생성
        self.agent = Agent(
            model="gemini-2.5-flash",
            name="weather_llm_agent",
            description="날씨 정보를 분석하고 마케팅 인사이트를 제공하는 LLM 에이전트",
            instruction=WEATHER_AGENT_INSTR,
            # tools=[WeatherTool(), ForecastTool()],  # 날씨 도구들 제공
        )

        # Runner 설정
        self.runner = Runner(
            app_name=self.agent.name,
            agent=self.agent,
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

        self.name = "weather_llm_agent"
        self.description = (
            "날씨 정보를 분석하고 마케팅 관점의 인사이트를 제공하는 LLM 에이전트"
        )

        print(f"Weather LLM Agent '{self.name}' initialized successfully.")

    async def run_async(self, *, args: Dict[str, Any]) -> Any:
        """Weather LLM Agent 실행"""
        try:
            request = args.get("request", "")
            if not request:
                return {"error": "요청 내용이 필요합니다"}

            print(f"Weather LLM Agent 실행: {request}")

            # 세션 생성
            session = await self.runner.session_service.create_session()

            # Agent 실행
            async for event in self.runner.run_async(
                session_id=session.session_id, user_input=request
            ):
                if hasattr(event, "response") and event.response:
                    result = {
                        "response": event.response,
                        "agent": self.name,
                        "status": "success",
                    }
                    print(f"Weather LLM Agent 응답: {event.response[:100]}...")
                    return result

            return {"error": "응답을 생성하지 못했습니다"}

        except Exception as e:
            print(f"Weather LLM Agent 실행 실패: {e}")
            return {"error": f"Weather LLM Agent 실행 실패: {str(e)}"}


# Weather LLM Agent Tool 인스턴스 생성
weather_llm_agent_tool = WeatherLLMAgentTool()

# MCP Server 생성
app = Server("weather-llm-agent-mcp-server")


@app.list_tools()
async def list_mcp_tools() -> List[mcp_types.Tool]:
    """MCP 도구 목록 반환"""
    print("MCP Server: Weather LLM Agent 도구 목록 요청")

    return [
        mcp_types.Tool(
            name=weather_llm_agent_tool.name,
            description=weather_llm_agent_tool.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "request": {
                        "type": "string",
                        "description": "날씨 관련 질문이나 분석 요청 (예: '서울 날씨 어때?', '부산 3일 예보 보고 마케팅 전략 추천해줘')",
                    }
                },
                "required": ["request"],
            },
        )
    ]


@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: Dict[str, Any]
) -> List[mcp_types.Content]:
    """MCP 도구 실행"""
    print(f"MCP Server: Weather LLM Agent 실행 요청 - {name}")

    if name == weather_llm_agent_tool.name:
        try:
            result = await weather_llm_agent_tool.run_async(args=arguments)
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            print(f"Weather LLM Agent 실행 오류: {e}")
            error_response = json.dumps(
                {"error": f"Weather LLM Agent 실행 실패: {str(e)}"}, ensure_ascii=False
            )
            return [mcp_types.TextContent(type="text", text=error_response)]
    else:
        error_response = json.dumps(
            {"error": f"알 수 없는 도구: {name}"}, ensure_ascii=False
        )
        return [mcp_types.TextContent(type="text", text=error_response)]


async def run_mcp_stdio_server():
    """MCP 서버를 stdio로 실행"""
    print("🤖 Weather LLM Agent MCP Server 시작...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-llm-agent-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    print("🌤️ Weather LLM Agent MCP Server 시작 중...")
    asyncio.run(run_mcp_stdio_server())
