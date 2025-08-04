# Payment Agent MCP Server Implementation
import asyncio
import json
from typing import Optional
from dotenv import load_dotenv

# MCP Server Imports
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from google.adk.tools.agent_tool import AgentTool

import mcp.server.stdio


import sys
import os


sys.path.append(os.path.dirname(__file__))
from custom_agent_tool import CustomAgentTool

# Load environment variables
load_dotenv()

# Payment Agent Instruction (similar to sub_agents pattern)
PAYMENT_AGENT_INSTR = """
당신은 결제 전문 에이전트입니다.

## 주요 역할
- 결제 관련 질문 응답
- 결제 프로세스 안내
- 결제 오류 해결 지원
- 결제 정책 설명

## 응답 스타일
- 명확하고 정확한 정보 제공
- 단계별 안내 제공
- 보안을 고려한 안전한 응답
- 사용자 친화적인 설명

## 제한사항
- 실제 결제 처리는 하지 않음
- 개인정보는 요청하지 않음
- 보안에 민감한 정보는 일반적인 안내만 제공
"""

payment_agent_tool = CustomAgentTool(instruction=PAYMENT_AGENT_INSTR)
# payment_agent_tool = AgentTool(
#     agent=Agent(
#         model="gemini-2.5-flash",
#         name="payment_agent",
#         description="A Payment Agent for handling payment-related queries and support",
#         instruction=PAYMENT_AGENT_INSTR,
#     )
# )

app = Server("payment-agent-mcp-server")


@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP 도구 목록 반환"""
    # MCP Tool 스키마 생성
    mcp_tool_schema = mcp_types.Tool(
        name=payment_agent_tool.name,
        description=payment_agent_tool.description,
        inputSchema={
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "결제 관련 질문이나 요청 내용",
                }
            },
            "required": ["request"],
        },
    )

    return [mcp_tool_schema]


@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict, tool_context: Optional[ToolContext] = None) -> list[mcp_types.Content]:
    """MCP 도구 실행"""
    # payment_agent_tool.tool_context = tool_context

    if name == payment_agent_tool.name:
        try:
            # PaymentAgentTool 실행
            result = await payment_agent_tool.run_async(
                args=arguments,
                tool_context=tool_context,
            )

            # MCP 응답 형식으로 변환
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp_types.TextContent(type="text", text=response_text)]

        except Exception as e:
            error_text = json.dumps(
                {"error": f"Payment Agent 실행 실패: {str(e)}"}, ensure_ascii=False
            )
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        error_text = json.dumps(
            {"error": f"도구 '{name}'을 찾을 수 없습니다."}, ensure_ascii=False
        )
        return [mcp_types.TextContent(type="text", text=error_text)]


# MCP Server 실행 함수
async def run_mcp_stdio_server():
    """MCP 서버를 stdio로 실행"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="payment-agent-mcp-server",
                server_version="1.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


# 메인 실행부
if __name__ == "__main__":
    asyncio.run(run_mcp_stdio_server())
