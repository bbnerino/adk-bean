from google.adk.tools.function_tool import FunctionTool
import logging
from typing import Optional

try:
    from pytrends.request import TrendReq
    import pandas as pd
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    logging.warning("pytrends 라이브러리가 설치되지 않았습니다. uv add pytrends로 설치해주세요.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _drop_is_partial(df):
    if df is not None and not df.empty and 'isPartial' in df.columns:
        return df.drop(columns=['isPartial'])
    return df


def _compute_trend_direction(recent_avg: float, past_avg: float) -> str:
    if past_avg <= 0:
        return "유지"
    change = (recent_avg - past_avg) / past_avg
    if change > 0.2:
        return "상승"
    elif change < -0.2:
        return "하락"
    else:
        return "유지"


def _analyze_seasonality(df) -> str:
    if df is None or df.empty or len(df) < 12:
        return "데이터 부족"
    
    try:
        # 간단한 계절성 분석: 월별 평균의 변동계수
        df_monthly = df.resample('M').mean()
        if len(df_monthly) < 4:
            return "비계절성"
        
        cv = df_monthly.std().iloc[0] / df_monthly.mean().iloc[0] if df_monthly.mean().iloc[0] > 0 else 0
        return "계절성" if cv > 0.3 else "비계절성"
    except:
        return "판단 불가"


def _analyze_trend_type(df_12m, df_3m) -> str:
    if df_12m is None or df_12m.empty:
        return "판단 불가"
    
    try:
        # 12개월 데이터의 최근 3개월과 이전 9개월 비교
        recent_3m_avg = df_12m.tail(90).mean().iloc[0] if len(df_12m) >= 90 else df_12m.tail(len(df_12m)//4).mean().iloc[0]
        past_9m_avg = df_12m.head(-90).mean().iloc[0] if len(df_12m) >= 90 else df_12m.head(len(df_12m)*3//4).mean().iloc[0]
        
        if past_9m_avg <= 0:
            return "판단 불가"
            
        change = (recent_3m_avg - past_9m_avg) / past_9m_avg
        
        # 급격한 상승/하락이면 일회성 가능성
        if abs(change) > 1.0:
            return "일회성"
        else:
            return "지속성"
    except:
        return "판단 불가"


def get_google_trend_data(keyword: str) -> str:
    """
    구글 트렌드 데이터 수집 및 분석
    
    고정 설정:
    - 지역: 미국 (US)
    - 기간: 최근 12개월 & 최근 3개월
    - 검색 유형: Web Search
    
    Args:
        keyword (str): 분석할 키워드
        
    Returns:
        str: 분석 결과 (최근 추이, 계절성, 일회성/지속성)
    """
    if not PYTRENDS_AVAILABLE:
        return "❌ pytrends 라이브러리가 설치되지 않았습니다. uv add pytrends로 설치해주세요."
    
    if not keyword or not keyword.strip():
        return "❌ 키워드를 입력해주세요."
    
    keyword = keyword.strip()
    
    try:
        # pytrends 초기화 (미국, 영어)
        pytrends = TrendReq(hl='en-US', tz=360)
        
        # 12개월 데이터 수집
        pytrends.build_payload([keyword], cat=0, timeframe='today 12-m', geo='US', gprop='')
        df_12m = pytrends.interest_over_time()
        df_12m = _drop_is_partial(df_12m)
        
        # 3개월 데이터 수집
        pytrends.build_payload([keyword], cat=0, timeframe='today 3-m', geo='US', gprop='')
        df_3m = pytrends.interest_over_time()
        df_3m = _drop_is_partial(df_3m)
        
        if (df_12m is None or df_12m.empty) and (df_3m is None or df_3m.empty):
            return f"❌ '{keyword}' 키워드에 대한 트렌드 데이터를 찾을 수 없습니다."
        
        # 분석 및 자연스러운 응답 생성
        if not df_12m.empty and not df_3m.empty:
            avg_12m = df_12m[keyword].mean()
            avg_3m = df_3m[keyword].mean()
            trend_direction = _compute_trend_direction(avg_3m, avg_12m)
            seasonality = _analyze_seasonality(df_12m)
            trend_type = _analyze_trend_type(df_12m, df_3m)
            
            # SEO 전략 관점의 상세 분석 응답
            trend_analysis = ""
            if trend_direction == "상승":
                trend_analysis = f"최근 3개월({avg_3m:.1f})이 12개월 평균({avg_12m:.1f})보다 높아 **상승 추세**입니다."
            elif trend_direction == "하락": 
                trend_analysis = f"최근 3개월({avg_3m:.1f})이 12개월 평균({avg_12m:.1f})보다 낮아 **하락 추세**입니다."
            else:
                trend_analysis = f"12개월 평균({avg_12m:.1f})과 3개월 평균({avg_3m:.1f})이 비슷하여 **안정적으로 유지**되고 있습니다."
            
            # 계절성 분석
            seasonality_analysis = ""
            if seasonality == "계절성":
                seasonality_analysis = "특정 시기에 검색량이 집중되는 **계절성 패턴**을 보입니다."
            elif seasonality == "비계절성":
                seasonality_analysis = "연중 **일정한 검색 수요**를 유지하고 있습니다."
            else:
                seasonality_analysis = "계절성 패턴을 명확히 판단하기 어렵습니다."
            
            # 지속성 분석  
            persistence_analysis = ""
            if trend_type == "지속성":
                persistence_analysis = "**장기적으로 지속되는 검색 수요**로 SEO 콘텐츠 전략에 적합합니다."
            elif trend_type == "일회성":
                persistence_analysis = "**일시적 관심 증가** 패턴으로 트렌드성 콘텐츠에 적합할 수 있습니다."
            else:
                persistence_analysis = "지속성 판단이 어려우나 추가 모니터링이 필요합니다."
            
            # SEO 전략 제안
            if trend_direction in ["상승", "유지"] and trend_type == "지속성":
                seo_recommendation = "✅ **SEO 콘텐츠 전략 채택 권장** - 장기적 가치가 높은 키워드입니다."
            elif seasonality == "계절성" and trend_type == "지속성":
                seo_recommendation = "⚠️ **조건부 채택** - 계절성을 고려한 콘텐츠 계획이 필요합니다."
            elif trend_direction == "하락" or trend_type == "일회성":
                seo_recommendation = "❌ **신중 검토 필요** - 단기 트렌드일 가능성이 높습니다."
            else:
                seo_recommendation = "⚠️ **추가 분석 필요** - 다른 지표와 함께 종합 판단하세요."
            
            return f"""📈 **'{keyword}' Google Trends 분석 (미국 기준)**

🔍 **검색 추이**: {trend_analysis}

📅 **계절성 분석**: {seasonality_analysis}

⏱️ **지속성 판단**: {persistence_analysis}

🎯 **SEO 전략 제안**: {seo_recommendation}"""
            
        else:
            return f"❌ '{keyword}' 키워드에 대한 충분한 트렌드 데이터를 찾을 수 없습니다."
        
    except Exception as e:
        logger.error(f"Google Trends 수집 중 오류: {e}")
        return f"❌ 처리 중 오류가 발생했습니다: {e}"


# FunctionTool 등록 (간단 버전)
google_trend_tool = FunctionTool(get_google_trend_data)
