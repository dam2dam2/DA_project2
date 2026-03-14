import requests
import pandas as pd
import time
import os
import json


def fetch_airportal_data(url, payload):
    """
    Airportal POST API 호출 함수
    """
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "request-call": "web-rest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Origin": "https://www.airportal.go.kr",
        "Referer": "https://www.airportal.go.kr/stats/transport/dailyRoute.do",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def collect_yearly_data(url, base_payload, start_year, end_year, indicator_name):
    """
    연도별로 루프를 돌며 데이터를 수집하는 함수
    """
    all_data = []
    print(f"--- {indicator_name} 데이터 수집 시작 ({start_year}-{end_year}) ---")

    for year in range(start_year, end_year + 1):
        print(f"{year}년 데이터 요청 중...")
        payload = base_payload.copy()
        payload["startDt"] = f"{year}0101"
        payload["endDt"] = f"{year}1231"

        # 2025년의 경우 12월 31일까지 데이터가 없을 수 있으므로 현재 날짜 등을 고려해야 할 수도 있으나
        # 요청한 범위대로 진행

        result = fetch_airportal_data(url, payload)
        if result and "content" in result:
            items = result["content"]
            if items:
                # 데이터에 연도 정보 추가
                for item in items:
                    item["year"] = year
                all_data.extend(items)
            else:
                print(f"{year}년 데이터가 비어있습니다.")

        # 서버 부하 방지를 위해 대기
        time.sleep(1)

    return pd.DataFrame(all_data)


def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    start_year = 2018
    end_year = 2025

    # 1. 일간 항공 운송 통계 수집
    print("\n[1] 일간 항공 운송 통계 수집 중...")
    daily_url = (
        "https://www.airportal.go.kr/stats/transport/getDailyAirTransportStats.do"
    )
    daily_payload = {}  # startDt, endDt는 collect_yearly_data에서 설정됨
    daily_df = collect_yearly_data(
        daily_url, daily_payload, start_year, end_year, "일간 항공 운송 통계"
    )

    if not daily_df.empty:
        daily_df.to_csv(
            "data/airportal_daily_transport_2018_2025.csv",
            index=False,
            encoding="utf-8-sig",
        )
        print(
            "공항별 일간 통계 저장 완료: data/airportal_daily_transport_2018_2025.csv"
        )

    # 2. 노선별 통계 - 국제선 (I)
    print("\n[2] 노선별 국제선 통계 수집 중...")
    route_url = (
        "https://www.airportal.go.kr/stats/transport/selectDailyStatisticsByRoute.do"
    )
    intl_payload = {"koreaAirport": "RKSI", "airlineType": "I"}
    intl_df = collect_yearly_data(
        route_url, intl_payload, start_year, end_year, "노선별 국제선 통계"
    )

    if not intl_df.empty:
        intl_df.to_csv(
            "data/airportal_route_international_2018_2025.csv",
            index=False,
            encoding="utf-8-sig",
        )
        print(
            "노선별 국제선 통계 저장 완료: data/airportal_route_international_2018_2025.csv"
        )

    # 3. 노선별 통계 - 국내선 (D)
    print("\n[3] 노선별 국내선 통계 수집 중...")
    dom_payload = {"koreaAirport": "RKSI", "airlineType": "D"}
    dom_df = collect_yearly_data(
        route_url, dom_payload, start_year, end_year, "노선별 국내선 통계"
    )

    if not dom_df.empty:
        dom_df.to_csv(
            "data/airportal_route_domestic_2018_2025.csv",
            index=False,
            encoding="utf-8-sig",
        )
        print(
            "노선별 국내선 통계 저장 완료: data/airportal_route_domestic_2018_2025.csv"
        )


if __name__ == "__main__":
    main()
