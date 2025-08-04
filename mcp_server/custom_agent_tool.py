from typing import Dict, Any, Optional

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService


class CustomAgentTool(BaseTool):
    """Agent를 BaseTool로 래핑한 클래스"""

    def __init__(self, instruction):
        # Agent 생성 (sub_agents 패턴과 동일)
        self.agent = Agent(
            model="gemini-2.5-flash",
            name="payment_agent",
            description="A Payment Agent for handling payment-related queries and support",
            instruction=instruction,
            tools=[],  # 필요시 결제 관련 도구 추가 가능
        )

        # BaseTool 초기화
        super().__init__(
            name="payment_agent",
            description="결제 관련 질문에 대한 전문적인 답변을 제공하는 에이전트",
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: Optional[ToolContext] = None
    ) -> Any:
        """
        AgentTool과 동일한 패턴으로 Agent 실행
        """
        try:
            # 입력 파라미터 추출
            request = args.get("request", "")
            if not request:
                return {"error": "요청 내용이 필요합니다."}

            # Content 생성 (AgentTool 패턴과 동일)
            from google.genai import types

            content = types.Content(
                role="user",
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
                user_id="payment_user",
                state={} if not tool_context else tool_context.state.to_dict(),
            )

            # Agent 실행
            last_event = None
            async for event in runner.run_async(
                user_id=session.user_id, session_id=session.id, new_message=content
            ):
                # 상태 업데이트 (tool_context가 있는 경우)
                if tool_context and event.actions.state_delta:
                    tool_context.state.update(event.actions.state_delta)
                last_event = event

            # 결과 반환
            if not last_event or not last_event.content or not last_event.content.parts:
                return {"error": "응답을 생성할 수 없습니다."}

            # 텍스트 결합
            response_text = "\n".join(
                p.text for p in last_event.content.parts if p.text
            )

            return {
                "status": "success",
                "response": response_text,
                "agent": self.agent.name,
            }

        except Exception as e:
            return {
                "error": f"Payment Agent 실행 중 오류 발생: {str(e)}",
                "status": "error",
            }
