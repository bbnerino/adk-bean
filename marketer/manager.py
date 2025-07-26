from typing import Dict, Optional, Tuple
import vertexai
from vertexai.preview import reasoning_engines
from marketer._agent import create_marketer_agent

class ADKAppManager:
    def __init__(self, project_id: str, location: str, staging_bucket: str):
        vertexai.init(
            project=project_id,
            location=location,
            staging_bucket=staging_bucket,
        )
        self.apps: Dict[str, reasoning_engines.AdkApp] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id

    def get_or_create_app(self, user_id: str, instruction: Optional[str] = None, tools: list = []) -> reasoning_engines.AdkApp:
        """사용자별 ADK 앱을 가져오거나 생성합니다."""
        if user_id not in self.apps:
            agent = create_marketer_agent(instruction, tools)
            self.apps[user_id] = reasoning_engines.AdkApp(
                agent=agent,
                enable_tracing=True,
            )
        return self.apps[user_id]

    def get_or_create_session(self, user_id: str, session_id: Optional[str] = None) -> Tuple[Optional[reasoning_engines.AdkApp], Optional[str]]:
        """사용자의 세션을 가져오거나 생성합니다."""
        app = self.apps.get(user_id)
        if not app:
            return None, None

        if session_id:
            return app, session_id
        
        if user_id in self.user_sessions:
            return app, self.user_sessions[user_id]
        
        session = app.create_session(user_id=user_id)
        self.user_sessions[user_id] = session.id
        return app, session.id 