"""
간단한 Google Trends Tool 사용 예시
고정 설정: US, 최근 12개월 & 3개월, Web Search
출력: 최근 추이(상승/하락/유지), 계절성, 일회성/지속성
"""

from google_trend_tool import get_google_trend_data


def main():
    keywords = [
        "iPhone",
        "NBA",
        "AI",
    ]

    for kw in keywords:
        print("=" * 60)
        print(get_google_trend_data(kw))


if __name__ == "__main__":
    main() 