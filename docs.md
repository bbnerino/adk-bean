# ADK Agent를 MCP 서버에서 BaseTool로 구현하기

## 개요

ADK의 Agent를 MCP(Model Context Protocol) 서버에서 BaseTool로 구현하여 기존 sub_agents와 동일한 방식으로 동작하게 할 수 있습니다. 이를 통해 Agent를 독립적인 서비스로 분리하면서도 기존 ADK 에코시스템과 완벽하게 통합할 수 있습니다.

## 구현 가능성

✅ **완전히 가능합니다!**

- ADK의 AgentTool 패턴을 MCP 서버에서 재현 가능
- 기존 sub_agents와 동일한 파라미터 처리 방식 지원
- Agent의 모든 기능(instruction, tools, memory) 유지
- MCP를 통한 원격 호출로 확장성 확보

## 핵심 아키텍처

```
Root Agent
    ↓
MCPToolset (payment_agent_tool)
    ↓ (stdio/network)
MCP Server (payment_agent.py)
    ↓
PaymentAgentTool (BaseTool)
    ↓
Agent (with instruction + tools)
```

## 구현 방법

### 1. PaymentAgentTool 클래스 생성

```python
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
```

### 2. AgentTool 패턴 재현

```python
async def run_async(self, *, args: Dict[str, Any], tool_context: Optional[ToolContext] = None) -> Any:
    """AgentTool과 동일한 패턴으로 Agent 실행"""
    
    # 1. 입력 파라미터 추출
    request = args.get('request', '')
    
    # 2. Content 생성 (AgentTool 패턴과 동일)
    from google.genai import types
    content = types.Content(
        role='user',
        parts=[types.Part.from_text(text=request)],
    )
    
    # 3. Runner 생성 및 실행 (AgentTool 패턴과 동일)
    runner = Runner(
        app_name=self.agent.name,
        agent=self.agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    # 4. 세션 생성 및 실행
    session = await runner.session_service.create_session(
        app_name=self.agent.name,
        user_id='payment_user',
        state={} if not tool_context else tool_context.state.to_dict(),
    )
    
    # 5. Agent 실행 및 이벤트 처리
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
    
    # 6. 결과 반환
    response_text = '\n'.join(
        p.text for p in last_event.content.parts if p.text
    )
    
    return {
        "status": "success",
        "response": response_text,
        "agent": self.agent.name
    }
```

### 3. MCP 서버 설정

```python
# MCP Server 설정
app = Server("payment-agent-mcp-server")

@app.list_tools()
async def list_mcp_tools() -> list[mcp_types.Tool]:
    """MCP 도구 목록 반환"""
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
    return [mcp_tool_schema]

@app.call_tool()
async def call_mcp_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    """MCP 도구 실행"""
    if name == payment_agent_tool.name:
        # PaymentAgentTool 실행
        result = await payment_agent_tool.run_async(
            args=arguments,
            tool_context=None,
        )
        
        # MCP 응답 형식으로 변환
        response_text = json.dumps(result, indent=2, ensure_ascii=False)
        return [mcp_types.TextContent(type="text", text=response_text)]
```

### 4. MCPToolset 연결

```python
# marketer/utils/mcp/payment_agent.py
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

payment_agent_tool = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["/Users/uneedcomms/Desktop/adk-bean/mcp_server/payment_agent.py"],
    )
)
```

## 기존 Sub_Agents와의 비교

### Sub_Agents (내부)
```python
# 직접 Agent 생성
content_writer_agent = Agent(
    model="gemini-2.5-flash",
    name="content_writer_agent",
    description="A Content Writing Agent for marketing content",
    instruction=CONTENT_WRITER_INSTR,
    tools=[update_content, patch_content],
)

# Root Agent에 직접 추가
sub_agents=[content_writer_agent]
```

### MCP Agent (외부)
```python
# MCP 서버에서 Agent 래핑
class PaymentAgentTool(BaseTool):
    def __init__(self):
        self.agent = Agent(...)  # 동일한 Agent 생성
        super().__init__(...)

# MCPToolset으로 연결
payment_agent_tool = MCPToolset(
    connection_params=StdioServerParameters(...)
)

# Root Agent에 도구로 추가
tools=[payment_agent_tool]
```

## 장점

### 1. 확장성
- Agent를 독립적인 서비스로 분리
- 다른 시스템에서도 재사용 가능
- 수평적 확장 가능

### 2. 유지보수성
- Agent별 독립적 배포 가능
- 버전 관리 용이
- 장애 격리

### 3. 호환성
- 기존 ADK 에코시스템과 완벽 호환
- 동일한 파라미터 처리 방식
- 기존 코드 수정 최소화

## 사용 예시

### Root Agent에서 호출
```python
# 기존 sub_agents와 동일한 방식으로 사용
root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    instruction=ROOT_AGENT_INSTR,
    sub_agents=[content_writer_agent],  # 내부 Agent
    tools=[payment_agent_tool],         # MCP Agent
)
```

### 실행 과정
1. 사용자: "결제 방법을 알려주세요"
2. Root Agent: payment_agent_tool 호출 결정
3. MCPToolset: MCP 서버와 통신
4. PaymentAgentTool: Agent 실행
5. Agent: 결제 관련 답변 생성
6. 결과 반환: Root Agent → 사용자

## 모범 사례

### 1. 명확한 역할 정의
```python
PAYMENT_AGENT_INSTR = """
당신은 결제 전문 에이전트입니다.

## 주요 역할
- 결제 관련 질문 응답
- 결제 프로세스 안내
- 결제 오류 해결 지원

## 제한사항
- 실제 결제 처리는 하지 않음
- 개인정보는 요청하지 않음
"""
```

### 2. 오류 처리
```python
try:
    result = await payment_agent_tool.run_async(args=arguments)
    return {"status": "success", "response": result}
except Exception as e:
    return {"error": f"Agent 실행 실패: {str(e)}", "status": "error"}
```

### 3. 상태 관리
```python
# tool_context를 통한 상태 공유 (필요시)
if tool_context and event.actions.state_delta:
    tool_context.state.update(event.actions.state_delta)
```

## 결론

ADK Agent를 MCP 서버에서 BaseTool로 구현하는 것은 완전히 가능하며, 다음과 같은 이점을 제공합니다:

- **기존 패턴 유지**: AgentTool과 동일한 동작 방식
- **확장성**: 독립적인 서비스로 분리
- **호환성**: 기존 ADK 에코시스템과 완벽 통합
- **유연성**: 필요에 따라 내부/외부 Agent 선택 가능

이를 통해 복잡한 시스템을 모듈화하면서도 ADK의 강력한 Multi-Agent 기능을 그대로 활용할 수 있습니다. 