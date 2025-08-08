# Google Trends Tool 사용 가이드

pytrends 라이브러리를 활용한 실제 구글 트렌드 데이터 수집 및 분석 도구입니다.

## 📋 목차

- [설치 및 설정](#설치-및-설정)
- [기본 사용법](#기본-사용법)
- [고급 기능](#고급-기능)
- [매개변수 설명](#매개변수-설명)
- [에러 처리](#에러-처리)
- [제한사항 및 주의사항](#제한사항-및-주의사항)

## 🚀 설치 및 설정

### 1. 의존성 설치

```bash
# pyproject.toml에 이미 포함됨
pip install pytrends pandas
```

### 2. 기본 import

```python
from deep_search.utils.tools.google_trend_tool import get_google_trend_data, GoogleTrendAnalyzer
```

## 📊 기본 사용법

### 1. 간단한 키워드 분석

```python
# 기본 사용 (한국 지역, 12개월 데이터)
result = get_google_trend_data("아이폰")
print(result)
```

### 2. 매개변수를 활용한 분석

```python
# 미국 지역, 5년 데이터, 포괄적 분석
result = get_google_trend_data(
    keyword="iPhone",
    timeframe="today 5-y",
    geo="US",
    analysis_type="comprehensive"
)
print(result)
```

## 🔧 고급 기능

### 1. GoogleTrendAnalyzer 클래스 직접 사용

```python
analyzer = GoogleTrendAnalyzer(hl='ko', tz=540)

# 시간별 관심도 데이터
trend_data = analyzer.get_interest_over_time(
    keywords=["아이폰", "갤럭시"],
    timeframe="today 12-m",
    geo="KR"
)

# 지역별 관심도 데이터
region_data = analyzer.get_interest_by_region(
    keywords=["치킨"],
    geo="KR",
    resolution="REGION"
)

# 관련 검색어
related = analyzer.get_related_queries(
    keyword="인공지능",
    geo="KR"
)
```

### 2. 트렌드 분석 기능

```python
# 트렌드 방향 분석 (상승/하락/유지)
direction = analyzer.analyze_trend_direction(trend_data, "아이폰")

# 계절성 분석
seasonality = analyzer.detect_seasonality(trend_data, "아이폰")

print(f"트렌드 방향: {direction}")
print(f"계절성: {seasonality}")
```

## 📝 매개변수 설명

### get_google_trend_data() 함수

| 매개변수 | 타입 | 기본값 | 설명 |
|---------|------|--------|------|
| `keyword` | str | 필수 | 분석할 키워드 |
| `timeframe` | str | 'today 12-m' | 검색 기간 |
| `geo` | str | 'KR' | 지역 코드 |
| `analysis_type` | str | 'comprehensive' | 분석 유형 |

### timeframe 옵션

```python
# 시간 기간 옵션들
'today 1-H'     # 지난 1시간
'today 4-H'     # 지난 4시간  
'today 1-d'     # 지난 1일
'today 7-d'     # 지난 7일
'today 1-m'     # 지난 1개월
'today 3-m'     # 지난 3개월
'today 12-m'    # 지난 12개월
'today 5-y'     # 지난 5년
'all'           # 모든 기간 (2004년부터)

# 사용자 정의 기간
'2023-01-01 2023-12-31'  # 2023년 전체
'2024-06-01 2024-08-31'  # 2024년 6-8월
```

### geo 옵션

```python
# 주요 국가 코드들
'KR'    # 대한민국
'US'    # 미국
'JP'    # 일본
'CN'    # 중국
'GB'    # 영국
'DE'    # 독일
'FR'    # 프랑스

# 지역별 세부 설정
'US-CA'    # 미국 캘리포니아
'US-NY'    # 미국 뉴욕
'KR-11'    # 한국 서울
```

### analysis_type 옵션

- `'comprehensive'`: 전체 분석 (기본값)
- `'trend_only'`: 트렌드만 분석
- `'region_only'`: 지역별 분석만

## 🔍 출력 결과 예시

```
📈 **아이폰 구글 트렌드 분석 결과**
🌍 지역: KR | 📅 기간: today 12-m

📊 **기본 통계:**
• 최대값: 100
• 평균값: 45.2
• 최소값: 12
• 데이터 포인트: 52개

📈 **트렌드 방향:** 상승
🔄 **계절성:** 계절성

📅 **최근 트렌드 (최근 5개 시점):**
• 2024-01-07: 78
• 2024-01-14: 82
• 2024-01-21: 89
• 2024-01-28: 95
• 2024-02-04: 100

🗺️ **지역별 관심도 (상위 5개):**
• 서울특별시: 100
• 부산광역시: 85
• 대구광역시: 72
• 인천광역시: 68
• 광주광역시: 55

🔍 **관련 검색어 (상위 5개):**
• 아이폰 15: 100
• 아이폰 가격: 85
• 아이폰 출시일: 72
• 아이폰 스펙: 65
• 아이폰 리뷰: 58

⏰ **데이터 수집 시간:** 2024-02-04 15:30:45
```

## ⚠️ 에러 처리

### 일반적인 에러 상황

1. **pytrends 라이브러리 미설치**
```
❌ pytrends 라이브러리가 설치되지 않았습니다. 'pip install pytrends'로 설치해주세요.
```

2. **검색량 부족**
```
❌ 'obscurekeyword123' 키워드에 대한 트렌드 데이터를 찾을 수 없습니다. 검색량이 너무 낮을 수 있습니다.
```

3. **요청 제한**
```
❌ 트렌드 데이터 분석 중 오류가 발생했습니다: 429 Too Many Requests
```

### 에러 대응 방법

```python
try:
    result = get_google_trend_data("키워드")
    if "❌" in result:
        print("에러 발생:", result)
    else:
        print("성공:", result)
except Exception as e:
    print(f"예외 발생: {e}")
```

## 🚫 제한사항 및 주의사항

### 1. 요청 제한
- **시간당 약 100-200 요청**
- **일일 약 1,400 요청** (4시간 timeframe 기준)
- 과도한 요청시 IP 차단 (24-48시간)

### 2. 데이터 제한
- 최대 **5개 키워드** 동시 비교
- 검색량이 매우 낮은 키워드는 데이터 없음
- 상대적 인기도 (0-100 스케일)

### 3. 안전한 사용법

```python
import time

# 요청 간격 조절
for keyword in keywords:
    result = get_google_trend_data(keyword)
    print(result)
    time.sleep(60)  # 1분 대기
```

### 4. 대규모 프로젝트용 권장사항

- **프록시 로테이션** 사용
- **캐싱 시스템** 구축
- **상용 API 서비스** 고려 (SearchAPI, DataForSEO 등)
- **분산 처리 시스템** 구축

## 🧪 테스트 실행

```bash
# 테스트 코드 실행
cd deep_search/utils/tools/
python google_trend_example.py
```

## 📞 지원 및 문의

- 이슈 발생시 GitHub Issues에 보고
- 기능 요청 및 개선사항 제안 환영
- pytrends 공식 문서: https://github.com/GeneralMills/pytrends

---

**주의**: 이 도구는 비공식 API를 사용하므로 구글 정책 변경에 따라 작동하지 않을 수 있습니다. 상용 프로젝트에서는 공식 데이터 소스나 상용 API 서비스 사용을 권장합니다. 