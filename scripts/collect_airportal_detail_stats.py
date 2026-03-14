import requests
import pandas as pd
import time
import os
import json


def fetch_airportal_detail(url, payload):
    """
    Airportal 상세 통계 POST API 호출 함수
    """
    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "request-call": "web-rest",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Origin": "https://www.airportal.go.kr",
        "Referer": "https://www.airportal.go.kr/stats/transport/chartDetail4.do",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching detail data: {e}")
        return None


def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    url = "https://www.airportal.go.kr/stats/transport/getDetailedAirTransportStats4.do"

    # 수집 조합 설정 (sn_gubun: 0-정기, 1-부정기 / pass_gubun: 1-유임, 3-환승 / arvl_type: D-출발, A-도착)
    combinations = [
        {
            "name": "정기-유임여객-출발",
            "sn_gubun": "0",
            "pass_gubun": "1",
            "arvl_type": "D",
        },
        {
            "name": "부정기-유임여객-출발",
            "sn_gubun": "1",
            "pass_gubun": "1",
            "arvl_type": "D",
        },
        {
            "name": "정기-유임여객-도착",
            "sn_gubun": "0",
            "pass_gubun": "1",
            "arvl_type": "A",
        },
        {
            "name": "부정기-유임여객-도착",
            "sn_gubun": "1",
            "pass_gubun": "1",
            "arvl_type": "A",
        },
        {
            "name": "정기-환승여객-도착",
            "sn_gubun": "0",
            "pass_gubun": "3",
            "arvl_type": "A",
        },
        {
            "name": "부정기-환승여객-도착",
            "sn_gubun": "1",
            "pass_gubun": "3",
            "arvl_type": "A",
        },
        {
            "name": "정기-환승여객-출발",
            "sn_gubun": "0",
            "pass_gubun": "3",
            "arvl_type": "D",
        },
        {
            "name": "부정기-환승여객-출발",
            "sn_gubun": "1",
            "pass_gubun": "3",
            "arvl_type": "D",
        },
    ]

    start_year = 2018
    end_year = 2025

    for combo in combinations:
        print(f"\n>>> 수집 작업 시작: {combo['name']}")
        all_combo_data = []

        for year in range(start_year, end_year + 1):
            print(f"  {year}년 데이터 수집 중...", end=" ", flush=True)
            for month in range(1, 13):
                ym = f"{year}{month:02d}"

                payload = {
                    "last_yearmonth": ym,
                    "this_yearmonth": ym,
                    "sn_gubun": combo["sn_gubun"],
                    "pass_gubun": combo["pass_gubun"],
                    "arvl_type": combo["arvl_type"],
                    "carge_gubun": "2",  # 참고 데이터상 고정값으로 보임
                }

                result = fetch_airportal_detail(url, payload)
                if result and "content" in result:
                    items = result["content"]
                    for item in items:
                        # 메타데이터 추가
                        item["year_month"] = ym
                        item["year"] = year
                        item["month"] = month
                        item["category_name"] = combo["name"]
                        all_combo_data.append(item)

                # 매 월 요청 후 짧은 대기
                time.sleep(0.1)
            print("완료")

        if all_combo_data:
            df = pd.DataFrame(all_combo_data)
            # 파일명에서 한글 및 특수문자 처리
            safe_name = combo["name"].replace("-", "_")
            filename = f"data/airportal_detail_{safe_name}_{start_year}_{end_year}.csv"
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"저장 완료: {filename} (총 {len(df)}행)")

        # 조합별 수집 사이 긴 대기
        time.sleep(1)


if __name__ == "__main__":
    main()
