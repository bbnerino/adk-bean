# ADK Sub_Agents 동작 방식 완전 가이드

## 목차
1. [Sub_Agents 개념 소개](#sub_agents-개념-소개)
2. [기본 구조와 관계](#기본-구조와-관계)
3. [위임 메커니즘](#위임-메커니즘)
4. [실행 과정](#실행-과정)
5. [협업 워크플로우](#협업-워크플로우)
6. [메모리와 컨텍스트 공유](#메모리와-컨텍스트-공유)
7. [고급 기능](#고급-기능)
8. [실제 구현 예시](#실제-구현-예시)
9. [모범 사례](#모범-사례)

---

## Sub_Agents 개념 소개

ADK(Agent Development Kit)의 **Sub_Agents**는 복잡한 작업을 여러 전문화된 에이전트가 협력하여 해결할 수 있게 해주는 핵심 기능입니다.

### 핵심 특징
- **자율성**: 각 Sub_Agent는 독립적인 실행 단위
- **전문성**: 특정 도메인에 특화된 기능 수행
- **협업성**: 다른 에이전트와 정보 공유 및 협력
- **계층성**: Parent-Child 관계를 통한 구조화된 관리
- **도구화**: AgentTool로 래핑되어 호출 가능한 도구가 됨

---

## 기본 구조와 관계

### Parent-Child 관계

```python
# BaseAgent에서 정의된 관계
class BaseAgent(BaseModel):
    parent_agent: Optional[BaseAgent] = Field(default=None, init=False)
    sub_agents: list[BaseAgent] = Field(default_factory=list)
```

### 계층 구조 예시

```
Root Agent (marketer_agent)
├── Content Writer Agent    # 콘텐츠 작성 전담
├── Content Reviewer Agent  # 콘텐츠 검토 전담  
├── SEO Optimizer Agent     # SEO 최적화 전담
└── Strategy Planner Agent  # 전략 기획 전담
```

### 에이전트 생성 방식

```python
# Sub_Agent 생성
def create_marketer_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="marketer_agent",
        description="A Marketing AI using the services of multiple sub-agents",
        instruction=ROOT_AGENT_INSTR,
        sub_agents=[
            content_writer.create_agent(),
            content_reviewer.create_agent(),
            seo_optimizer.create_agent(),
            strategy_planner.create_agent(),
        ],
        tools=tools,
    )
```

---

## 위임 메커니즘

### AgentTool을 통한 위임

Sub_agents는 **AgentTool**로 래핑되어 Root Agent가 호출할 수 있는 도구가 됩니다:

```python
class AgentTool(BaseTool):
    """A tool that wraps an agent.
    
    This tool allows an agent to be called as a tool within a larger application.
    The agent's input schema is used to define the tool's input parameters, and
    the agent's output is returned as the tool's result.
    """
    
    def __init__(self, agent: BaseAgent, skip_summarization: bool = False):
        self.agent = agent
        self.skip_summarization: bool = skip_summarization
        super().__init__(name=agent.name, description=agent.description)
```

### 동적 에이전트 발견

```python
def find_agent(self, name: str) -> Optional[BaseAgent]:
    """에이전트 트리에서 특정 이름의 에이전트를 찾습니다."""
    if self.name == name:
        return self
    return self.find_sub_agent(name)

def find_sub_agent(self, name: str) -> Optional[BaseAgent]:
    """하위 에이전트에서 특정 이름의 에이전트를 찾습니다."""
    for sub_agent in self.sub_agents:
        if result := sub_agent.find_agent(name):
            return result
    return None
```

---

## 실행 과정

### 1단계: 요청 분석 및 에이전트 선택

Root Agent의 LLM이 사용자 요청을 분석하고 적절한 sub_agent를 선택합니다:

```python
# Root Agent의 프롬프트에서 역할 구분
ROOT_AGENT_INSTR = """
## 에이전트 역할 구분
1. Content Writer 전용 작업:
   - 실제 콘텐츠 작성만 담당
   - 설명이나 질문 없이 순수 콘텐츠만 작성

2. 다른 에이전트 작업:
   - Strategy Planner: 전략 설명, 방향성 제시, 질문
   - SEO Optimizer: 키워드 제안, 최적화 방안 설명
   - Content Reviewer: 피드백 제공, 개선점 설명
"""
```

### 2단계: AgentTool을 통한 실행

선택된 sub_agent가 AgentTool을 통해 실행됩니다:

```python
# AgentTool의 run_async 메서드 실행 과정
async def run_async(self, *, args: dict[str, Any], tool_context: ToolContext) -> Any:
    # 1. 입력 검증 및 변환
    content = types.Content(
        role='user',
        parts=[types.Part.from_text(text=args['request'])],
    )
    
    # 2. Runner 생성 및 실행
    runner = Runner(
        app_name=self.agent.name,
        agent=self.agent,
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )
    
    # 3. 세션 생성 및 실행
    session = await runner.session_service.create_session(
        app_name=self.agent.name,
        user_id='tmp_user',
        state=tool_context.state.to_dict(),
    )
    
    # 4. 이벤트 스트림 처리
    async for event in runner.run_async(
        user_id=session.user_id, 
        session_id=session.id, 
        new_message=content
    ):
        if event.actions.state_delta:
            tool_context.state.update(event.actions.state_delta)
        last_event = event
    
    # 5. 결과 반환
    return tool_result
```

### 3단계: 결과 통합 및 응답

Sub_agent의 실행 결과가 Root Agent로 반환되어 최종 응답에 통합됩니다.

---

## 협업 워크플로우

### 순차적 협업 패턴

```python
# 작업 프로세스 예시
"""
1. Strategy Planner가 사용자의 요구사항을 파악하고 질문합니다
2. 필요한 전문 에이전트들이 각자의 분석과 제안을 제시합니다
3. Content Writer는 다른 에이전트들의 인사이트를 바탕으로 순수 콘텐츠만 작성합니다
4. Content Reviewer가 피드백을 제공합니다
5. 필요한 경우 Content Writer가 수정된 콘텐츠를 다시 작성합니다
"""
```

### 실행 흐름도

```
사용자 요청 
    ↓
Root Agent (요청 분석)
    ↓
LLM 판단 (어떤 Sub_Agent 호출할지 결정)
    ↓
AgentTool 실행 (선택된 Sub_Agent 실행)
    ↓
Sub_Agent 작업 수행
    ↓
결과 반환 및 통합
    ↓
최종 응답 생성
```

ADK Sub_Agents의 동작 방식을 체계적으로 정리한 문서를 작성했습니다. 이 문서는 다음과 같은 내용을 포함합니다:

1. **개념 소개**: Sub_Agents의 핵심 특징
2. **구조와 관계**: Parent-Child 관계 및 계층 구조
3. **위임 메커니즘**: AgentTool을 통한 위임 방식
4. **실행 과정**: 3단계 실행 프로세스
5. **협업 워크플로우**: 순차적 협업 패턴
6. **메모리와 컨텍스트**: 상태 공유 메커니즘
7. **고급 기능**: 조건부 실행 및 탐색 기능
8. **실제 구현**: Content Writer, Strategy Planner 예시
9. **모범 사례**: 개발 시 고려사항

이 문서를 통해 ADK Sub_Agents의 동작 방식을 완전히 이해하고 실제 프로젝트에 적용할 수 있을 것입니다.

---

## 메모리와 컨텍스트 공유

### 상태 공유 메커니즘

```python
# Tool Context를 통한 상태 공유
if event.actions.state_delta:
    tool_context.state.update(event.actions.state_delta)
```

### 세션 관리

```python
# 각 Sub_Agent는 독립적인 세션을 가지지만 상태는 공유
session = await runner.session_service.create_session(
    app_name=self.agent.name,
    user_id='tmp_user',
    state=tool_context.state.to_dict(),  # 부모의 상태 전달
)
```

### 메모리 서비스

- **InMemorySessionService**: 세션 간 연속성 유지
- **InMemoryMemoryService**: 단기 메모리 관리
- **ForwardingArtifactService**: 아티팩트 전달

---

## 고급 기능

### 조건부 실행 흐름

```python
@property
def _llm_flow(self) -> BaseLlmFlow:
    if (
        self.disallow_transfer_to_parent
        and self.disallow_transfer_to_peers
        and not self.sub_agents
    ):
        return SingleFlow()  # 단일 실행
    else:
        return AutoFlow()    # 자동 흐름 제어
```

### Root Agent 탐색

```python
@property
def root_agent(self) -> BaseAgent:
    """Gets the root agent of this agent."""
    root_agent = self
    while root_agent.parent_agent is not None:
        root_agent = root_agent.parent_agent
    return root_agent
```

---

## 실제 구현 예시

### Content Writer Agent

```python
def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="content_writer_agent",
        description="A Content Writing Agent for marketing content",
        instruction=CONTENT_WRITER_INSTR,
        tools=[update_content, patch_content],
    )

CONTENT_WRITER_INSTR = """
당신은 콘텐츠 작가 에이전트입니다.

## 주요 역할
- 마케팅 콘텐츠 작성
- 광고 문구 작성
- SNS 포스트 작성

## 클라이언트 요구사항
- 전체 콘텐츠를 출력할 경우 update_content tool 을 사용해야 합니다
- 콘텐츠를 수정할 경우 patch_content tool 을 사용해야 합니다
- 콘텐츠를 출력할 경우, 설명 없이 콘텐츠만 출력해야 합니다
"""
```

### Strategy Planner Agent

```python
def create_agent():
    return Agent(
        model="gemini-2.5-flash",
        name="strategy_planner_agent",
        description="A Strategy Planning Agent for marketing campaigns",
        instruction=STRATEGY_PLANNER_INSTR,
        tools=[calculate_mcp],
    )

STRATEGY_PLANNER_INSTR = """
당신은 전략 기획 에이전트입니다.

## 주요 역할
- 마케팅 목표 정의 및 KPI 설정
- 캠페인 전략 설계 및 로드맵 수립
- 작업 분해 및 일정 관리

## 출력 형식
- 명확한 마케팅 목표 및 KPI
- 단계별 캠페인 로드맵
- 작업 분해 및 담당자 배정
"""
```

---

## 모범 사례

### 1. 명확한 역할 분담

```python
# 각 에이전트의 역할을 명확히 정의
- Content Writer: 순수 콘텐츠 작성만
- Strategy Planner: 전략 수립 및 질문
- Content Reviewer: 검토 및 피드백
- SEO Optimizer: 최적화 방안 제안
```

### 2. 적절한 도구 할당

```python
# 에이전트별로 필요한 도구만 할당
content_writer_tools = [update_content, patch_content]
strategy_planner_tools = [calculate_mcp]
seo_optimizer_tools = [keyword_research, meta_optimizer]
```

### 3. 상태 관리

```python
# 상태 변경사항을 적절히 공유
if event.actions.state_delta:
    tool_context.state.update(event.actions.state_delta)
```

### 4. 오류 처리

```python
# 각 Sub_Agent 실행 시 오류 처리
try:
    result = await sub_agent.run_async(context)
except Exception as e:
    logger.error(f"Sub_Agent {sub_agent.name} failed: {e}")
    # 대체 로직 또는 오류 응답
```

### 5. 성능 최적화

```python
# 불필요한 Sub_Agent 호출 방지
if not self.sub_agents:
    return SingleFlow()  # 직접 실행
else:
    return AutoFlow()    # Sub_Agent 위임 가능
```

---

## 결론

ADK의 Sub_Agents 시스템은 복잡한 작업을 여러 전문 에이전트가 협력하여 해결할 수 있게 해주는 강력한 아키텍처입니다. 

**주요 장점:**
- **모듈성**: 각 에이전트를 독립적으로 개발/관리
- **전문성**: 특정 업무에 특화된 에이전트 구성
- **확장성**: 필요에 따라 새로운 에이전트 추가
- **재사용성**: 다양한 시스템에서 에이전트 재활용
- **유지보수성**: 각 에이전트별 독립적 업데이트

이러한 특징들로 인해 ADK Sub_Agents는 실제 프로덕션 환경에서 복잡한 비즈니스 로직을 효과적으로 구현할 수 있는 뛰어난 솔루션입니다.
