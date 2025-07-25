from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import vertexai
from vertexai.preview import reasoning_engines
from google.adk.agents import Agent
from marketer._agent import create_marketer_agent

# Google Cloud 프로젝트 설정
PROJECT_ID = "geo-project-467010"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://geo-project-adk-staging"

# FastAPI 앱 생성
app = FastAPI(title="ADK Agent API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정하세요
    allow_credentials=True,
    allow_methods=["*"],  # 필요한 HTTP 메서드만 지정하세요 (예: ["GET", "POST"])
    allow_headers=["*"],  # 필요한 헤더만 지정하세요
)


# 요청/응답 모델
class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    instruction: Optional[str] = None
    tools: Optional[list] = []

class ChatResponse(BaseModel):
    session_id: str
    messages: List[dict]


@app.post("/api/v1/adk/marketer", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        vertexai.init(
            project=PROJECT_ID,
            location=LOCATION,
            staging_bucket=STAGING_BUCKET,
        )

        # 매 요청마다 새로운 마케터 에이전트 인스턴스 생성
        agent = create_marketer_agent(request.instruction, request.tools)
        adk_app = reasoning_engines.AdkApp(
            agent=agent,
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
