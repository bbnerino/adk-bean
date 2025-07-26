from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from marketer.manager import ADKAppManager

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

# ADK 앱 매니저 인스턴스 생성
adk_manager = ADKAppManager(
    project_id=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
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
        # ADK 앱 가져오기 또는 생성
        adk_app = adk_manager.get_or_create_app(
            user_id=request.user_id,
            instruction=request.instruction,
            tools=request.tools
        )

        # 세션 가져오기 또는 생성
        adk_app, session_id = adk_manager.get_or_create_session(
            user_id=request.user_id,
            session_id=request.session_id
        )

        if not adk_app or not session_id:
            raise HTTPException(status_code=500, detail="Failed to create or get session")

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
