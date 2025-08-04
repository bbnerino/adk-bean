"""
ADK Tools for Weather Agent
공식 문서 기반 구현
"""

import json
import random
from typing import Dict, Any
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext


class WeatherTool(BaseTool):
    """날씨 정보를 가져오는 ADK Tool"""

    def __init__(self):
        super().__init__(
            name="get_weather", description="특정 도시의 현재 날씨 정보를 가져옵니다"
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext = None
    ) -> Any:
        """날씨 정보 조회"""
        try:
            city = args.get("city", "")
            if not city:
                return {"error": "도시 이름이 필요합니다"}

            # 실제로는 Weather API를 호출하지만, 데모용으로 mock 데이터 사용
            weather_conditions = ["맑음", "흐림", "비", "눈", "안개"]
            temperature = random.randint(-10, 35)
            condition = random.choice(weather_conditions)
            humidity = random.randint(30, 90)

            return {
                "city": city,
                "temperature": f"{temperature}°C",
                "condition": condition,
                "humidity": f"{humidity}%",
                "status": "success",
            }

        except Exception as e:
            return {"error": f"날씨 정보 조회 실패: {str(e)}"}


class ForecastTool(BaseTool):
    """일기예보 정보를 가져오는 ADK Tool"""

    def __init__(self):
        super().__init__(
            name="get_forecast", description="특정 도시의 3일 일기예보를 가져옵니다"
        )

    async def run_async(
        self, *, args: Dict[str, Any], tool_context: ToolContext = None
    ) -> Any:
        """일기예보 조회"""
        try:
            city = args.get("city", "")
            days = args.get("days", 3)

            if not city:
                return {"error": "도시 이름이 필요합니다"}

            # Mock 일기예보 데이터
            forecast = []
            weather_conditions = ["맑음", "흐림", "비", "눈"]

            for i in range(min(days, 7)):  # 최대 7일
                forecast.append(
                    {
                        "day": f"Day {i+1}",
                        "temperature_high": random.randint(15, 30),
                        "temperature_low": random.randint(5, 15),
                        "condition": random.choice(weather_conditions),
                        "precipitation": f"{random.randint(0, 80)}%",
                    }
                )

            return {"city": city, "forecast": forecast, "status": "success"}

        except Exception as e:
            return {"error": f"일기예보 조회 실패: {str(e)}"}
