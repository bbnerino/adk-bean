# Makefile for ADK Bean Project
.PHONY: help dev install payment weather web clean

# 메인 개발 서버 실행
dev:
	uv run python main.py

# 의존성 설치
install:
	uv sync

# Web Tool MCP 서버 실행
web:
	uv run adk web

# 캐시 파일 정리
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true