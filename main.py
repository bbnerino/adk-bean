from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import vertexai
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent
from marketer.agent import root_agent as marketer_agent

# Google Cloud 프로젝트 설정
PROJECT_ID = "geo-project-467010"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://geo-project-adk-staging"

# FastAPI 앱 생성
app = FastAPI(title="ADK Agent API")


# 요청/응답 모델
class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    instruction: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    messages: List[dict]


# ADK 에이전트 생성
def create_sample_agent(instruction: str = None):
    """에이전트를 생성합니다."""
    if instruction is None:
        instruction = "사용자의 질문에 친절하게 답변하는 에이전트입니다."

    return Agent(
        name="sample_agent",
        model="gemini-2.0-flash",
        description="전문적이고 친절한 한국어 AI 어시스턴트입니다.",
        instruction=instruction,
        tools=[],
    )


@app.post("/api/v1/adk/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )

        adk_app = reasoning_engines.AdkApp(
            # agent=marketer_agent,
            agent=create_sample_agent(request.instruction),
            enable_tracing=True,
        )

        # 세션이 없으면 새로 생성
        if not request.session_id:
            session = adk_app.create_session(user_id=request.user_id)
            session_id = session.id
        else:
            session_id = request.session_id

        # 쿼리 실행
        messages = []
        for event in adk_app.stream_query(
            user_id=request.user_id,
            session_id=session_id,
            message=request.message,
        ):
            messages.append(event)

        return ChatResponse(session_id=session_id, messages=messages)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
