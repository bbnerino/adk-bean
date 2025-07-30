from typing import List, Optional, Any
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from google.genai import types
import vertexai
import os
from marketer._agent import create_marketer_agent
import traceback

from marketer.utils.tools.patch_content import patch_content
from marketer.utils.tools.update_content import update_content

# 환경변수 로드
load_dotenv()



db_type = "mysql+pymysql"
db_user = "root"
db_password = "uneed3515"
db_host = "localhost"
db_port = 3306
db_name = "adk_sessions"

# db_path = "sqlite:///database/adk-db.sqlite"
db_path = f"{db_type}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
session_service = DatabaseSessionService(db_path)

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
    agent=create_marketer_agent(),
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


@app.post("/api/v1/adk/marketer", response_model=ChatResponse)
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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
