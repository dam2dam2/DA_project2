import requests
import pandas as pd
import time
import os
import xml.etree.ElementTree as ET

# 공공데이터포털 API 설정
SERVICE_KEY = "51702d087f409b7a148989988f3c18e39ed43fad1b831de7978d69a0b2d42330"


def fetch_data(url_pattern, indicator_name, from_month, to_month, **kwargs):
    """
    API로부터 데이터를 가져오는 함수
    """
    params = {
        "serviceKey": SERVICE_KEY,
        "from_month": from_month,
        "to_month": to_month,
        "periodicity": "0",
        "type": "xml",
    }
    params.update(kwargs)

    try:
        response = requests.get(url_pattern, params=params)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching {indicator_name} for {from_month}-{to_month}: {e}")
        return None


def parse_xml_to_df(xml_data, indicator_name):
    """
    XML 데이터를 파싱하여 데이터프레임으로 변환하는 함수
    """
    if not xml_data:
        return pd.DataFrame()

    try:
        root = ET.fromstring(xml_data)
        items = []

        # XML 구조에 따라 데이터 추출 (보통 <item> 태그 내에 데이터가 존재)
        for item in root.findall(".//item"):
            data = {}
            for child in item:
                data[child.tag] = child.text
            items.append(data)

        return pd.DataFrame(items)
    except Exception as e:
        print(f"Error parsing XML for {indicator_name}: {e}")
        return pd.DataFrame()


def collect_data_all_years(url_pattern, indicator_name, **kwargs):
    """
    2002년부터 2025년까지 전체 데이터를 수집하는 함수
    지나치게 긴 기간을 한 번에 요청하면 오류가 날 수 있으므로 연도별로 수집합니다.
    """
    all_dfs = []
    print(f"--- {indicator_name} 데이터 수집 시작 ---")

    for year in range(2002, 2026):
        from_month = f"{year}01"
        to_month = f"{year}12"

        # 2026년은 현재 시점(2026-03-12) 기준으로 데이터가 없을 수 있으므로 2025년까지만 수집하도록 유도됨
        # 하지만 API가 월별로 정확한 기간을 지원하므로 연도별로 끊어서 수집
        print(f"{year}년 데이터 요청 중...")
        xml_data = fetch_data(
            url_pattern, indicator_name, from_month, to_month, **kwargs
        )
        df = parse_xml_to_df(xml_data, indicator_name)

        if not df.empty:
            # 연도(year) 컬럼 추가
            df["year"] = year
            all_dfs.append(df)

        # API 과부하 방지를 위해 짧은 대기 시간 추가
        time.sleep(0.5)

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()


def main():
    # 데이터 저장 경로 확인
    if not os.path.exists("data"):
        os.makedirs("data")

    # 1. 운항편 수 수집
    # API: getTotalNumberOfFlight
    flight_url = (
        "https://apis.data.go.kr/B551177/AviationStatsByTimeline/getTotalNumberOfFlight"
    )
    flight_df = collect_data_all_years(
        flight_url, "운항편_수", pax_cargo="Y", domestic_foreign="I"
    )
    if not flight_df.empty:
        flight_df.to_csv(
            "data/airport_flights_2002_2025.csv", index=False, encoding="utf-8-sig"
        )
        print("운항편 수 저장 완료: data/airport_flights_2002_2025.csv")

    # 2. 여객수 수집
    # API: getTotalNumberOfPassenger
    passenger_url = "https://apis.data.go.kr/B551177/AviationStatsByTimeline/getTotalNumberOfPassenger"
    passenger_df = collect_data_all_years(
        passenger_url, "여객수", domestic_foreign="I", passenger_type="1"
    )
    if not passenger_df.empty:
        passenger_df.to_csv(
            "data/airport_passengers_2002_2025.csv", index=False, encoding="utf-8-sig"
        )
        print("여객수 저장 완료: data/airport_passengers_2002_2025.csv")

    # 3. 화물량 수집
    # API: getTotalTonsOfCargo
    cargo_url = (
        "https://apis.data.go.kr/B551177/AviationStatsByTimeline/getTotalTonsOfCargo"
    )
    cargo_df = collect_data_all_years(
        cargo_url, "화물량", pax_cargo="Y", domestic_foreign="I", baggage_type="1"
    )
    if not cargo_df.empty:
        cargo_df.to_csv(
            "data/airport_cargo_2002_2025.csv", index=False, encoding="utf-8-sig"
        )
        print("화물량 저장 완료: data/airport_cargo_2002_2025.csv")


if __name__ == "__main__":
    main()
