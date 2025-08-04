"""
Weather MCP Tool for Marketer Agent
기존 Weather MCP 서버를 연결하는 도구
"""

import os
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

# 프로젝트 루트 경로 계산
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
weather_server_path = os.path.join(
    project_root, "mcp_server", "weather_agent", "mcp_server.py"
)

# Weather MCP 서버 연결 설정
weather_agent = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", weather_server_path],
        ),
        timeout=30.0,  # 충분한 타임아웃 설정
    )
)
