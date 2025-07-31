from google.adk.sessions.database_session_service import (
    DatabaseSessionService,
    StorageSession,
    StorageEvent,
    StorageAppState,
    StorageUserState
)

class MarketDatabaseSessionService(DatabaseSessionService):
    def __init__(self, db_url: str, **kwargs):
        # 기존 클래스의 테이블 이름을 직접 변경
        StorageSession.__table__.name = "market_sessions"
        StorageEvent.__table__.name = "market_events"
        StorageAppState.__table__.name = "market_app_states"
        StorageUserState.__table__.name = "market_user_states"
        
        # 부모 클래스 초기화
        super().__init__(db_url, **kwargs) 