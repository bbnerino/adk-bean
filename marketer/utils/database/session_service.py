from google.adk.sessions.database_session_service import (
    DatabaseSessionService, 
    Base,
    StorageSession,
    StorageEvent,
    StorageAppState,
    StorageUserState
)

class MarketBase(Base):
    __abstract__ = True
    
class MarketStorageSession(StorageSession):
    __tablename__ = "market_sessions"
    
class MarketStorageEvent(StorageEvent):
    __tablename__ = "market_events"
    __table_args__ = (
        ForeignKeyConstraint(
            ["app_name", "user_id", "session_id"],
            ["market_sessions.app_name", "market_sessions.user_id", "market_sessions.id"],
            ondelete="CASCADE",
        ),
    )
    
class MarketStorageAppState(StorageAppState):
    __tablename__ = "market_app_states"
    
class MarketStorageUserState(StorageUserState):
    __tablename__ = "market_user_states"

class MarketDatabaseSessionService(DatabaseSessionService):
    def __init__(self, db_url: str, **kwargs):
        super().__init__(db_url, **kwargs)
        # 기존 테이블 대신 새로운 테이블 사용
        MarketBase.metadata.create_all(self.db_engine) 