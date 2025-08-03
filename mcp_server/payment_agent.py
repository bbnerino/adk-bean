# Payment Agent MCP Server Implementation
import asyncio
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# MCP Server Imports
from mcp import types as mcp_types
from mcp.server.lowlevel import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# ADK Imports
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

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

class PaymentAgentTool(BaseTool):
    """Payment Agent를 BaseTool로 래핑한 클래스"""
    
    def __init__(self):
        # Agent 생성 (sub_agents 패턴과 동일)
        self.agent = Agent(
            model="gemini-2.5-flash",
            name="payment_agent",
            description="A Payment Agent for handling payment-related queries and support",
            instruction=PAYMENT_AGENT_INSTR,
            tools=[],  # 필요시 결제 관련 도구 추가 가능
        )
        
        # BaseTool 초기화
        super().__init__(
            name="payment_agent",
            description="결제 관련 질문에 대한 전문적인 답변을 제공하는 에이전트"
        )
    
    async def run_async(self, *, args: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Any:
        """
        AgentTool과 동일한 패턴으로 Agent 실행
        """
        try:
            # 입력 파라미터 추출
            request = args.get('request', '')
            if not request:
                return {"error": "요청 내용이 필요합니다."}
            
            # Content 생성 (AgentTool 패턴과 동일)
            from google.genai import types
            content = types.Content(
                role='user',
                parts=[types.Part.from_text(text=request)],
            )
            
            # Runner 생성 및 실행 (AgentTool 패턴과 동일)
            runner = Runner(
                app_name=self.agent.name,
                agent=self.agent,
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )
            
            # 세션 생성
            session = await runner.session_service.create_session(
                app_name=self.agent.name,
                user_id='payment_user',
                state={} if not tool_context else tool_context.state.to_dict(),
            )
            
            # Agent 실행
            last_event = None
            async for event in runner.run_async(
                user_id=session.user_id,
                session_id=session.id,
                new_message=content
            ):
                # 상태 업데이트 (tool_context가 있는 경우)
                if tool_context and event.actions.state_delta:
                    tool_context.state.update(event.actions.state_delta)
                last_event = event
            
            # 결과 반환
            if not last_event or not last_event.content or not last_event.content.parts:
                return {"error": "응답을 생성할 수 없습니다."}
            
            # 텍스트 결합
            response_text = '\n'.join(
                p.text for p in last_event.content.parts if p.text
            )
            
            return {
                "status": "success",
                "response": response_text,
                "agent": self.agent.name
            }
            
        except Exception as e:
            return {
                "error": f"Payment Agent 실행 중 오류 발생: {str(e)}",
                "status": "error"
            }

# PaymentAgentTool 인스턴스 생성
print("Initializing Payment Agent Tool...")
payment_agent_tool = PaymentAgentTool()
print(f"Payment Agent Tool '{payment_agent_tool.name}' initialized and ready.")

# MCP Server 설정
print("Creating MCP Server instance...")
app = Server("payment-agent-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP 도구 목록 반환"""
    print("MCP Server: Received list_tools request.")
    
    # MCP Tool 스키마 생성
    mcp_tool_schema = mcp_types.Tool(
        name=payment_agent_tool.name,
        description=payment_agent_tool.description,
        inputSchema={
            "type": "object",
            "properties": {
                "request": {
                    "type": "string",
                    "description": "결제 관련 질문이나 요청 내용"
                }
            },
            "required": ["request"]
        }
    )
    
    print(f"MCP Server: Advertising tool: {mcp_tool_schema.name}")
    return [mcp_tool_schema]

@app.call_tool()
async def call_mcp_tool(
    name: str, arguments: dict
) -> list[mcp_types.Content]:
    """MCP 도구 실행"""
    print(f"MCP Server: Received call_tool request for '{name}' with args: {arguments}")
    
    if name == payment_agent_tool.name:
        try:
            # PaymentAgentTool 실행
            result = await payment_agent_tool.run_async(
                args=arguments,
                tool_context=None,
            )
            print(f"MCP Server: Payment Agent executed. Response: {result}")
            
            # MCP 응답 형식으로 변환
            response_text = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp_types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            print(f"MCP Server: Error executing Payment Agent: {e}")
            error_text = json.dumps(
                {"error": f"Payment Agent 실행 실패: {str(e)}"},
                ensure_ascii=False
            )
            return [mcp_types.TextContent(type="text", text=error_text)]
    else:
        print(f"MCP Server: Tool '{name}' not found.")
        error_text = json.dumps(
            {"error": f"도구 '{name}'을 찾을 수 없습니다."},
            ensure_ascii=False
        )
        return [mcp_types.TextContent(type="text", text=error_text)]

# MCP Server 실행 함수
async def run_mcp_stdio_server():
    """MCP 서버를 stdio로 실행"""
    print("Starting Payment Agent MCP Server...")
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
    print("Payment Agent MCP Server starting...")
    asyncio.run(run_mcp_stdio_server())
