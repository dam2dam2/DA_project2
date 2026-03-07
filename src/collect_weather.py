import requests
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

# 설정
SERVICE_KEY = "51702d087f409b7a148989988f3c18e39ed43fad1b831de7978d69a0b2d42330"
STN_IDS = "108"  # 서울
URL = "http://apis.data.go.kr/1360000/AsosHourlyInfoService/getWthrDataList"
OUTPUT_DIR = "/Users/dami/innercircle/DA_project2/data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "seoul_weather_2015_2025.csv")


def fetch_weather_period(start_dt, end_dt):
    """특정 기간의 기상 데이터를 가져옵니다 (API 제한상 분할 요청 필요)"""
    params = {
        "serviceKey": SERVICE_KEY,
        "pageNo": "1",
        "numOfRows": "999",  # 최대 요청 수
        "dataType": "JSON",  # JSON 권장
        "dataCd": "ASOS",
        "dateCd": "HR",
        "startDt": start_dt.strftime("%Y%m%d"),
        "startHh": "01",
        "endDt": end_dt.strftime("%Y%m%d"),
        "endHh": "23",
        "stnIds": STN_IDS,
    }

    try:
        response = requests.get(URL, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data["response"]["header"]["resultCode"] == "00":
                items = data["response"]["body"]["items"]["item"]
                return pd.DataFrame(items)
            else:
                print(f"API Error: {data['response']['header']['resultMsg']}")
        else:
            print(f"HTTP Error: {response.status_code}")
    except Exception as e:
        print(f"Request Error: {e}")
    return pd.DataFrame()


def collect_all_weather():
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2025, 12, 31)

    # 현재 서버 환경 시간을 고려하여 종료일 조정 (오늘 날짜까지만)
    current_time = datetime.now()
    if end_date > current_time:
        end_date = current_time - timedelta(days=1)

    all_dfs = []
    current_dt = start_date

    # 30일 단위로 끊어서 요청 (너무 크게 잡으면 타임아웃 발생 가능)
    delta = timedelta(days=30)

    print(
        f"Starting weather data collection from {start_date.date()} to {end_date.date()}..."
    )

    while current_dt <= end_date:
        next_dt = min(current_dt + delta, end_date)
        print(
            f"Fetching: {current_dt.strftime('%Y-%m-%d')} ~ {next_dt.strftime('%Y-%m-%d')}"
        )

        df_chunk = fetch_weather_period(current_dt, next_dt)
        if not df_chunk.empty:
            all_dfs.append(df_chunk)

        current_dt = next_dt + timedelta(days=1)
        time.sleep(0.1)  # API 부하 방지

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)

        # 컬럼 이름 변경 및 타입 변환
        # tm: 일시, ta: 기온, rn: 강수량, ws: 풍속, hm: 습도
        # 필요한 항목만 추출
        cols = {
            "tm": "datetime",
            "ta": "temp",
            "rn": "precip",
            "ws": "wind_speed",
            "hm": "humidity",
        }

        # 실제 존재하는 컬럼만 필터링
        existing_cols = [c for c in cols.keys() if c in final_df.columns]
        final_df = final_df[existing_cols].copy()
        final_df.rename(columns={c: cols[c] for c in existing_cols}, inplace=True)

        # 수치형 변환 (빈 문자열은 0 또는 NaN으로)
        for col in ["temp", "precip", "wind_speed", "humidity"]:
            if col in final_df.columns:
                final_df[col] = pd.to_numeric(final_df[col], errors="coerce").fillna(0)

        # 날짜별 집계 (시간별 -> 일별)
        final_df["date"] = pd.to_datetime(final_df["datetime"]).dt.date

        daily_df = (
            final_df.groupby("date")
            .agg(
                {
                    "temp": "mean",
                    "precip": "sum",
                    "wind_speed": "mean",
                    "humidity": "mean",
                }
            )
            .reset_index()
        )

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        daily_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"Saved {len(daily_df)} days of weather data to {OUTPUT_FILE}")
    else:
        print("Failed to collect any data.")


if __name__ == "__main__":
    # requests가 없을 수 있으므로 설치 확인 필요
    collect_all_weather()
