from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

CALCULATOR_SCRIPT = "marketer/utils/mcp/tools/calculate.py"

calculate_mcp = MCPToolset(
    connection_params=StdioServerParameters(
        command="python",
        args=[CALCULATOR_SCRIPT],
    ),
)
