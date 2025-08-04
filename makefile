# Makefile for ADK Bean Project
.PHONY: help dev install payment weather web clean


# 메인 개발 서버 실행
dev:
	uv run python main.py

# 의존성 설치
install:
	uv sync

# Payment Agent MCP 서버 실행
payment:
	uv run python mcp_server/payment_agent.py

# Weather Agent MCP 서버 실행
weather:
	uv run python mcp_server/weather_agent/weather_agent.py

# Web Tool MCP 서버 실행
web:
	uv run python mcp_server/load_web_tool.py

# 캐시 파일 정리
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true