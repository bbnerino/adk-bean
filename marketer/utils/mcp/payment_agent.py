from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

payment_agent_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="uv",
            args=["run", "python", "/Users/uneedcomms/Desktop/adk-bean/mcp_server/payment_agent.py"],
        ),
        timeout=30.0  # 5초 → 30초로 증가
    )
)

