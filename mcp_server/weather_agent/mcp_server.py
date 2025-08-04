"""
ADK Tools를 MCP Server로 노출
공식 문서의 "Share ADK Tools as MCP Server" 패턴 구현
"""

import asyncio
import json
from typing import List, Dict, Any
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK Tools import
from weather_tools import WeatherTool, ForecastTool

# ADK Tools 인스턴스 생성
weather_tool = WeatherTool()
forecast_tool = ForecastTool()

# 사용 가능한 도구들
available_tools = {"get_weather": weather_tool, "get_forecast": forecast_tool}

# MCP Server 생성
app = Server("weather-agent-mcp-server")


def adk_to_mcp_tool_type(adk_tool) -> mcp_types.Tool:
    """
    ADK Tool을 MCP Tool 스키마로 변환
    공식 문서에서 제시하는 유틸리티 함수 패턴
    """
    if adk_tool.name == "get_weather":
        return mcp_types.Tool(
            name=adk_tool.name,
            description=adk_tool.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "날씨를 조회할 도시 이름"}
                },
                "required": ["city"],
            },
        )
    elif adk_tool.name == "get_forecast":
        return mcp_types.Tool(
            name=adk_tool.name,
            description=adk_tool.description,
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "일기예보를 조회할 도시 이름",
                    },
                    "days": {
                        "type": "integer",
                        "description": "예보 일수 (1-7일)",
                        "minimum": 1,
                        "maximum": 7,
                        "default": 3,
                    },
                },
                "required": ["city"],
            },
        )


@app.list_tools()
async def list_tools() -> List[mcp_types.Tool]:
    """
    사용 가능한 도구 목록 반환
    공식 문서 패턴: @app.list_tools() 핸들러 구현
    """
    print("MCP Server: 도구 목록 요청 받음")

    mcp_tools = []
    for tool_name, adk_tool in available_tools.items():
        mcp_tool = adk_to_mcp_tool_type(adk_tool)
        mcp_tools.append(mcp_tool)
        print(f"MCP Server: 도구 등록 - {mcp_tool.name}")

    return mcp_tools


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> List[mcp_types.Content]:
    """
    도구 실행 핸들러
    공식 문서 패턴: @app.call_tool() 핸들러 구현
    """
    print(f"MCP Server: 도구 실행 요청 - {name}, 인수: {arguments}")

    if name in available_tools:
        try:
            # ADK Tool 실행
            adk_tool = available_tools[name]
            result = await adk_tool.run_async(args=arguments, tool_context=None)

            print(f"MCP Server: 도구 실행 완료 - {name}")

            # MCP 응답 형식으로 변환
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            print(f"MCP Server: 도구 실행 오류 - {name}: {e}")
            error_response = json.dumps(
                {"error": f"도구 실행 실패: {str(e)}"}, ensure_ascii=False
            )
            return [mcp_types.TextContent(type="text", text=error_response)]
    else:
        print(f"MCP Server: 알 수 없는 도구 - {name}")
        error_response = json.dumps(
            {"error": f"알 수 없는 도구: {name}"}, ensure_ascii=False
        )
        return [mcp_types.TextContent(type="text", text=error_response)]


async def run_mcp_stdio_server():
    """
    MCP 서버를 stdio로 실행
    공식 문서 패턴
    """
    print("Weather Agent MCP Server 시작...")
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="weather-agent-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    print("🌤️ Weather Agent MCP Server 시작 중...")
    asyncio.run(run_mcp_stdio_server())
