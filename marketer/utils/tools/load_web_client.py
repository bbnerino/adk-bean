from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters


PATH_TO_YOUR_MCP_SERVER_SCRIPT = "marketer/utils/tools/load_web_server.py"

load_web_client = MCPToolset(
    connection_params=StdioServerParameters(
        command="python3",  # Command to run your MCP server script
        args=[PATH_TO_YOUR_MCP_SERVER_SCRIPT],  # Argument is the path to the script
    )
    # tool_filter=['load_web_page'] # Optional: ensure only specific tools are loaded
)
