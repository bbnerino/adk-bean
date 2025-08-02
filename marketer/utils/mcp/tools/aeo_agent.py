from mcp.server.fastmcp import FastMCP
from google.adk.agents import Agent
from google.genai import types
import json

mcp = FastMCP("aeo_agent")

# AEO 전문 에이전트 초기화
aeo_brain = Agent(
    model="gemini-2.5-flash",
    name="aeo_brain",
    description="Answer Engine Optimization 전문 에이전트",
    instruction="""
    당신은 AEO(Answer Engine Optimization) 전문가입니다.
    Google의 Featured Snippet과 People Also Ask 섹션을 목표로 컨텐츠를 최적화합니다.
    
    다음 원칙들을 따라 작업하세요:
    1. 사용자 의도 중심
        - 검색 의도 정확히 파악
        - 명확하고 직접적인 답변 제공
        - 관련 후속 질문 예측
    
    2. Featured Snippet 최적화
        - 단락형: 40-50단어의 명확한 정의/설명
        - 목록형: 단계별/항목별 구조화
        - 표 형식: 비교/데이터 정리
    
    3. 구조화된 데이터
        - Schema.org 마크업 활용
        - FAQPage, HowTo 등 적절한 스키마 선택
        - 구조화된 데이터 검증
    
    4. 컨텐츠 품질
        - E-E-A-T 원칙 준수
        - 최신 정보 반영
        - 신뢰할 수 있는 데이터 기반
    """,
)

async def get_agent_response(prompt: str) -> dict:
    """에이전트로부터 응답을 받아 처리합니다."""
    message = types.Content(parts=[types.Part(text=prompt)])
    response = await aeo_brain.run_async(
        user_id="aeo_user",
        session_id="aeo_session",
        new_message=message
    )
    
    try:
        return json.loads(response.text)
    except json.JSONDecodeError:
        # 텍스트 응답을 구조화
        lines = response.text.split("\n")
        result = {}
        current_section = ""
        
        for line in lines:
            if line.endswith(":"):
                current_section = line[:-1].lower().replace(" ", "_")
                result[current_section] = []
            elif line.strip() and current_section:
                result[current_section].append(line.strip())
        
        return result

@mcp.tool()
async def analyze_content(content: str) -> dict:
    """컨텐츠를 분석하여 AEO 관점의 개선점을 찾습니다."""
    prompt = f"""
    다음 컨텐츠를 AEO 관점에서 분석하세요:
    
    {content}
    
    JSON 형식으로 다음 정보를 제공하세요:
    1. 주요 주제와 검색 의도
    2. 예상되는 사용자 질문들 (최소 3개)
    3. Featured Snippet 최적화 가능성과 추천 유형
    4. 구체적인 개선 제안
    5. 경쟁 컨텐츠 대비 차별화 포인트
    """
    
    return await get_agent_response(prompt)

@mcp.tool()
async def optimize_for_featured_snippet(
    content: str,
    target_question: str,
    snippet_type: str = "paragraph"
) -> dict:
    """컨텐츠를 Featured Snippet에 최적화합니다."""
    prompt = f"""
    다음 컨텐츠를 Featured Snippet 형식으로 최적화하세요:
    
    컨텐츠: {content}
    목표 질문: {target_question}
    스니펫 유형: {snippet_type}
    
    JSON 형식으로 다음 정보를 제공하세요:
    1. 최적화된 컨텐츠 (스니펫 유형에 맞게 구조화)
    2. Schema.org 마크업 (완성된 JSON-LD 형식)
    3. 최적화 세부사항 (단어 수, 구조, 키포인트 등)
    4. 추가 최적화 제안
    """
    
    return await get_agent_response(prompt)

@mcp.tool()
async def generate_aeo_strategy(keywords: list[str]) -> dict:
    """주어진 키워드에 대한 AEO 전략을 수립합니다."""
    prompt = f"""
    다음 키워드들에 대한 AEO 전략을 수립하세요:
    {', '.join(keywords)}
    
    JSON 형식으로 다음 정보를 제공하세요:
    1. 각 키워드별 최적의 컨텐츠 전략
    2. 예상되는 Featured Snippet 기회
    3. 권장되는 컨텐츠 구조와 포맷
    4. 차별화 전략과 경쟁 분석
    5. 구체적인 실행 계획
    """
    
    return await get_agent_response(prompt)

if __name__ == "__main__":
    mcp.run()
