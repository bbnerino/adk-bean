from typing import List, Optional, Any, Dict
from dotenv import load_dotenv
from google.adk.runners import Runner
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from google.genai import types
import vertexai
import os
import traceback
import urllib.parse
from datetime import datetime

from marketer.agent import root_agent
from marketer.utils.tools.patch_content import patch_content
from marketer.utils.tools.update_content import update_content
from marketer.utils.database.session_service import MarketDatabaseSessionService

# 환경변수 로드
load_dotenv()



db_type = "mysql+pymysql"
db_user = "root"
db_password = "uneed3515"
db_host = "localhost"
db_port = 3306
db_name = "adk_sessions"

db_path = "sqlite:///database/adk-db.sqlite"
# db_path = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
session_service = MarketDatabaseSessionService(db_path)

APP_NAME = "geo-project"
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "geo-project-467010")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING_BUCKET = "gs://geo-project-adk-staging"

# vertexai 초기화
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

app = FastAPI(title="ADK Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Runner 초기화는 vertexai 초기화 후에
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


class ChatRequest(BaseModel):
    user_id: str
    message: str
    session_id: Optional[str] = None
    instruction: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    messages: List[Any]  # Event 객체를 허용하도록 Any 타입 사용

    class Config:
        arbitrary_types_allowed = True  # 커스텀 타입 허용


class SessionInfo(BaseModel):
    session_id: str
    app_name: str
    user_id: str
    last_update_time: str


class SessionsListResponse(BaseModel):
    sessions: List[SessionInfo]


class SessionEventsResponse(BaseModel):
    session_id: str
    events: List[Any]  # 원본 Event 객체를 그대로 반환
    
    class Config:
        arbitrary_types_allowed = True  # 커스텀 타입 허용


@app.post("/api/v1/adk/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 세션 관리
        if request.session_id:
            try:
                # 기존 세션 조회
                session = await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=request.user_id,
                    session_id=request.session_id,
                )
                if not session:
                    # 세션이 없으면 새로 생성
                    session = await session_service.create_session(
                        app_name=APP_NAME, user_id=request.user_id
                    )
            except Exception as e:
                print(f"Session error: {str(e)}")
                print(traceback.format_exc())
                # 세션 조회/생성 실패 시 새로운 세션 생성
                session = await session_service.create_session(
                    app_name=APP_NAME, user_id=request.user_id
                )
        else:
            # 세션 ID가 없는 경우 새로운 세션 생성
            session = await session_service.create_session(
                app_name=APP_NAME, user_id=request.user_id
            )

        runner.agent.instruction = request.instruction

        content = types.Content(role="user", parts=[types.Part(text=request.message)])

        # 비동기로 실행
        messages = []
        try:
            async for event in runner.run_async(
                user_id=request.user_id, session_id=session.id, new_message=content
            ):
                messages.append(event)
        except Exception as e:
            print(f"Runner error: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail={
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc(),
                },
            )

        if not messages:
            raise HTTPException(
                status_code=500, detail="No response generated from the agent"
            )

        return ChatResponse(session_id=session.id, messages=messages)
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            },
        )


@app.get("/api/v1/adk/sessions/{user_id}", response_model=SessionsListResponse)
async def get_user_sessions(user_id: str):
    """특정 사용자의 모든 세션 리스트를 반환합니다."""
    try:
        # URL 디코딩 처리 (google-oauth2%7C106148396882803932962 -> google-oauth2|106148396882803932962)
        decoded_user_id = urllib.parse.unquote(user_id)
        
        # session_service의 편의 메서드를 사용하여 세션 리스트 가져오기
        sessions = await session_service.get_user_sessions(
            app_name=APP_NAME,
            user_id=decoded_user_id
        )
        
        # Session 객체들을 SessionInfo 모델로 변환
        session_infos = []
        for session in sessions:
            # last_update_time 처리 - float일 경우 datetime으로 변환
            last_update_str = ""
            if session.last_update_time:
                if isinstance(session.last_update_time, float):
                    # Unix timestamp (float)를 datetime으로 변환
                    dt = datetime.fromtimestamp(session.last_update_time)
                    last_update_str = dt.isoformat()
                elif hasattr(session.last_update_time, 'isoformat'):
                    # 이미 datetime 객체인 경우
                    last_update_str = session.last_update_time.isoformat()
                else:
                    # 기타 경우는 문자열로 변환
                    last_update_str = str(session.last_update_time)
            
            session_info = SessionInfo(
                session_id=session.id,
                app_name=session.app_name,
                user_id=session.user_id,
                last_update_time=last_update_str
            )
            session_infos.append(session_info)
        
        return SessionsListResponse(sessions=session_infos)
    except Exception as e:
        print(f"Sessions list error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            },
        )


@app.get("/api/v1/adk/sessions/{user_id}/{session_id}/events", response_model=SessionEventsResponse)
async def get_session_events(user_id: str, session_id: str):
    """특정 세션의 모든 이벤트를 반환합니다."""
    try:
        # URL 디코딩 처리
        decoded_user_id = urllib.parse.unquote(user_id)
        decoded_session_id = urllib.parse.unquote(session_id)
        
        # 세션과 이벤트들을 가져오기
        session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=decoded_user_id,
            session_id=decoded_session_id
        )
        
        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {decoded_session_id} for user {decoded_user_id}"
            )
        
        # 원본 Event 객체들을 그대로 반환
        return SessionEventsResponse(
            session_id=decoded_session_id,
            events=session.events
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Session events error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "traceback": traceback.format_exc(),
            },
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
