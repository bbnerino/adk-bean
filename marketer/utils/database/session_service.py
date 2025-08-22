from typing import List
from google.adk.sessions.database_session_service import (
    DatabaseSessionService,
    StorageSession,
    StorageEvent,
    StorageAppState,
    StorageUserState
)
from google.adk.sessions.session import Session
from google.adk.sessions.base_session_service import ListSessionsResponse

class MarketDatabaseSessionService(DatabaseSessionService):
    def __init__(self, db_url: str, **kwargs):
        # 기존 클래스의 테이블 이름을 직접 변경
        StorageSession.__table__.name = "market_sessions"
        StorageEvent.__table__.name = "market_events"
        StorageAppState.__table__.name = "market_app_states"
        StorageUserState.__table__.name = "market_user_states"
        
        # 부모 클래스 초기화
        super().__init__(db_url, **kwargs)
    
    async def get_user_sessions(self, app_name: str, user_id: str) -> List[Session]:
        """사용자의 모든 세션을 가져오는 편의 메서드"""
        sessions_response = await self.list_sessions(app_name=app_name, user_id=user_id)
        return sessions_response.sessions 