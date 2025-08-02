from google.adk.tools.mcp_tool.mcp_toolset import (
    MCPToolset,
    StdioServerParameters,
)


load_web_tool = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=["/Users/uneedcomms/Desktop/adk-bean/mcp_server/load_web_tool.py"],
    )
)
