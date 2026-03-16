import requests
import pandas as pd
import os
import time


def collect_route_data():
    url = "https://www.airportal.go.kr/stats/transport/getDetailedAirTransportStats3.do"

    headers = {
        "Content-Type": "application/json;charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.airportal.go.kr/stats/transport/chartDetail3.do",
    }

    # 수집 기간 설정: 2018-01 ~ 2025-12
    start_year = 2018
    end_year = 2025

    all_data = []

    os.makedirs("data", exist_ok=True)
    output_file = "data/airportal_route_intl_detailed_2018_2025.csv"

    print(f">>> 국제선 노선별 데이터 수집 시작 ({start_year} ~ {end_year})")

    for year in range(start_year, end_year + 1):
        for month in range(1, 13):
            year_month = f"{year}{month:02d}"

            # forreign_airport_gubun="total" 시 상세 리스트 반환 확인됨 (ICN 기준)
            payload = {
                "last_yearmonth": year_month,
                "this_yearmonth": year_month,
                "sn_gubun": "0",  # 정기선
                "airport_gubun": "ICN",  # 인천공항 기준
                "pass_gubun": "1",  # 여객
                "carge_gubun": "2",  # 화물
                "forreign_airport_gubun": "total",
                "di_gubun": "I",  # 국제선
                "arvl_type": "total",
            }

            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    content = data.get("content", [])

                    count = 0
                    for item in content:
                        # "전체 합계" 및 요약 행 제외
                        if item.get("code_name") in ["전체 합계", None] or not item.get(
                            "code_name"
                        ):
                            continue

                        item["year_month"] = year_month
                        # 필드명 클렌징 (숫자형 데이터)
                        for field in ["pass", "cargo", "flight_cnt"]:
                            if field in item and item[field]:
                                val = str(item[field]).replace(",", "")
                                if val.replace("-", "").isdigit():
                                    item[field] = int(val)
                                else:
                                    item[field] = 0

                        all_data.append(item)
                        count += 1

                    if count > 0:
                        print(f"[{year_month}] {count}개 노선 데이터 수집 완료.")
                    else:
                        print(f"[{year_month}] 데이터 없음.")
                else:
                    print(f"[{year_month}] Error: {response.status_code}")
            except Exception as e:
                print(f"[{year_month}] Exception: {e}")

            time.sleep(0.4)

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(output_file, index=False, encoding="utf-8-sig")

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f">>> 최종 수집 완료: {output_file} (총 {len(all_data)}건)")
    else:
        print(">>> 수집된 데이터가 없습니다.")


if __name__ == "__main__":
    collect_route_data()
