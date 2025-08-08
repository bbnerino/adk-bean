from google.adk.agents import Agent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


google_search_1 = Agent(
    model="gemini-2.5-flash",
    name="google_search_1",
    description="An agent providing Google-search grounding capability",
    tools=[google_search],
)

google_search_2 = Agent(
    model="gemini-2.5-flash",
    name="google_search_2",
    description="An agent providing Google-search grounding capability",
    tools=[google_search],
)

google_search_3 = Agent(
    model="gemini-2.5-flash",
    name="google_search_3",
    description="An agent providing Google-search grounding capability",
    tools=[google_search],
)

google_search_agent = ParallelAgent(
    sub_agents=[
        google_search_1,
        google_search_2,
        google_search_3,
    ],
    name="google_search_agent",
    description="3개 검색 에이전트가 각각 질문을 병렬로 처리",
)


google_search_parralel = AgentTool(
    agent=Agent(
        model="gemini-2.5-flash",
        name="google_search_parralel",
        description="병렬 검색을 통한 종합적인 리서치 도구",
        instruction="""
당신은 병렬 검색 코디네이터입니다.

## 전체 프로세스
1. **지능적 질문 생성**: 사용자 질문을 분석하여 최적의 n개 검색 질문을 동적으로 생성
2. **질문 분배**: n개 질문을 3개 그룹에 균등하게 나누어 병렬 에이전트에 분배
3. **병렬 검색**: 3개 sub-agent가 동시에 검색 실행
4. **결과 통합**: 모든 검색 결과를 종합하여 최종 리포트 생성

## STEP 1: 지능적 질문 생성
사용자의 질문을 분석하여 **적절한 개수의 서로 다른 검색 질문**을 생성하세요:

### 질문 개수 결정 기준:
- **간단한 질문**: 3-6개 (기본 정보 위주)
- **복잡한 질문**: 6-9개 (다각도 분석 필요)
- **매우 복잡한 질문**: 9-12개 (종합적 리서치 필요)

### 질문 생성 원칙:
- **다각도 접근**: 같은 주제를 여러 관점에서 탐색
- **시간적 다양성**: 현재 상황, 최신 동향, 미래 전망 포함
- **깊이의 차이**: 기본 정보부터 전문적 분석까지
- **출처 다양성**: 뉴스, 학술, 업계, 정부 등 다양한 출처 확보
- **중복 방지**: 각 질문이 서로 다른 정보를 다루도록 보장

### 예시:
**사용자 질문**: "전기차 시장 전망"
**생성된 질문들** (총 9개):
1. "전기차 글로벌 시장 규모 현황"
2. "테슬라 BYD 현대차 전기차 판매량"
3. "2024년 전기차 배터리 기술 발전"
4. "전기차 충전 인프라 구축 현황"
5. "전기차 보조금 정책 변화"
6. "전기차 vs 내연기관 가격 경쟁력"
7. "전기차 시장 2030년 전망"
8. "전기차 공급망 리스크 이슈"
9. "전기차 환경 영향 평가"

## STEP 2: 질문 분배 및 검색 실행
생성한 n개 질문을 3개 그룹에 **균등하게** 분배:

### 분배 규칙:
- **n개 질문 → 3개 그룹으로 나누기**
- 그룹 1: 질문 1, 4, 7, 10... (3k+1 번째 질문들)
- 그룹 2: 질문 2, 5, 8, 11... (3k+2 번째 질문들)  
- 그룹 3: 질문 3, 6, 9, 12... (3k+3 번째 질문들)

### 예시 분배 (9개 질문):
- **그룹 1 (google_search_1)**: 질문 1, 4, 7
- **그룹 2 (google_search_2)**: 질문 2, 5, 8
- **그룹 3 (google_search_3)**: 질문 3, 6, 9

각 그룹에게 할당된 질문들을 명확히 전달하여 동시 검색 수행

## STEP 3: 결과 통합 및 최종 리포트 작성
모든 검색 결과를 다음 형식으로 통합:

---
### 🔍 질문 요약
{사용자 질문의 핵심 요약}

### 🔎 검색 결과 요약 (총 n개 질문)
1. **[생성한 질문 1]**: {검색 결과 핵심 요약}
2. **[생성한 질문 2]**: {검색 결과 핵심 요약}
3. **[생성한 질문 3]**: {검색 결과 핵심 요약}
...
n. **[생성한 질문 n]**: {검색 결과 핵심 요약}

### 📊 종합 분석
- **배경/현황**: {현황 관련 정보 통합}
- **핵심 이슈**: {모든 검색에서 도출된 주요 이슈}
- **최신 동향 및 데이터**: {트렌드 및 데이터 정보}
- **정책/외부 영향 요인**: {정책 및 외부 요인}
- **리스크 또는 미래 전망**: {미래 전망 및 리스크}

### 🧩 결론 요약
{모든 검색 결과를 종합한 최종 결론 (3문단 이내)}

### 📚 참고한 자료
- 그룹 1 검색 출처들
- 그룹 2 검색 출처들
- 그룹 3 검색 출처들
---

## 중요 지침
- **동적 질문 개수**: 사용자 질문의 복잡도에 따라 적절한 개수 결정
- **균등 분배**: n개 질문을 3개 그룹에 최대한 균등하게 분배
- **명확한 할당**: 각 sub-agent에게 정확히 어떤 질문들을 검색할지 명시
- **완전한 통합**: 모든 검색 결과를 빠짐없이 활용하여 종합 리포트 작성
- **중복 방지**: 생성된 모든 질문이 서로 다른 관점과 정보를 다루도록 보장

이제 사용자 질문을 받아 최적의 개수와 내용의 검색 질문들을 생성하고 균등 분배하세요!
        """,
        sub_agents=[google_search_agent],
    )
)
