from google.adk.agents import Agent

from multi_tool_agent.function.get_current_time import get_current_time
from multi_tool_agent.function.get_weather import get_weather


root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_current_time],
)
