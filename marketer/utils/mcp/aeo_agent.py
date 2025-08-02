from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

AEO_SCRIPT = "/Users/uneedcomms/Desktop/adk-bean/marketer/utils/mcp/tools/aeo_agent.py"

aeo_agent = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=[AEO_SCRIPT],
    ),
)
