import requests
import pandas as pd
import os
import io
import time
from datetime import datetime

# 설정
AUTH_KEY = "oEmrXAvHS5yJq1wLx1ucSg"
STN_ID = "108"  # 서울
BASE_URL = "https://apihub.kma.go.kr/api/typ01/url/{endpoint}.php"
OUTPUT_PATH = (
    "/Users/dami/innercircle/DA_project2/data/seoul_weather_apihub_2015_2025.csv"
)


def fetch_apihub_data(endpoint, start_date, end_date):
    """API HUB에서 데이터를 가져와 DataFrame으로 반환합니다."""
    params = {
        "tm1": start_date,
        "tm2": end_date,
        "stn_id": STN_ID,
        "help": "0",
        "authKey": AUTH_KEY,
    }
    url = BASE_URL.format(endpoint=endpoint)

    try:
        response = requests.get(url, params=params, timeout=60)
        if response.status_code == 200:
            content = response.text
            # 주석(#)과 마지막 구분자(=) 제거
            lines = [
                line
                for line in content.split("\n")
                if line and not line.startswith("#") and line.strip() != "="
            ]

            # 헤더 추출 (도움말이 꺼져있으면 헤더가 안나올 수 있음, help=0 일 때 첫 줄이 데이터인지 확인)
            # 도움말 켜서 헤더만 따로 가져오기
            header_response = requests.get(
                url, params={**params, "help": "1"}, timeout=30
            )
            header_line = ""
            for line in header_response.text.split("\n"):
                if line.startswith("#    YMD"):
                    header_line = line.replace("#", "").strip()
                    break

            if not header_line:
                print(f"Header not found for {endpoint}")
                return pd.DataFrame()

            # CSV로 읽기
            csv_data = header_line + "\n" + "\n".join(lines)
            df = pd.read_csv(io.StringIO(csv_data))
            return df
        else:
            print(f"HTTP Error {response.status_code} for {endpoint}")
    except Exception as e:
        print(f"Error fetching {endpoint}: {e}")
    return pd.DataFrame()


def collect_combined_weather():
    endpoints = {
        "sts_ta": "temp",  # TA_DAVG
        "sts_rn": "precip",  # RN_DAY
        "sts_ws": "wind",  # WS_AVG
        "sts_hm": "humid",  # HM_AVG
    }

    # 2015년부터 2025년까지
    start_date = "20150101"
    end_date = "20251231"

    combined_df = None

    for endpoint, label in endpoints.items():
        print(f"Fetching {label} data from {endpoint}...")
        df = fetch_apihub_data(endpoint, start_date, end_date)

        if df.empty:
            print(f"Failed to fetch {label}")
            continue

        # 필요한 컬럼만 추출 및 이름 변경
        df["date"] = pd.to_datetime(df["YMD"], format="%Y%m%d").dt.date

        val_col = ""
        if endpoint == "sts_ta":
            val_col = "TA_DAVG"
        elif endpoint == "sts_rn":
            val_col = "RN_DAY"
        elif endpoint == "sts_ws":
            val_col = "WS_AVG"
        elif endpoint == "sts_hm":
            val_col = "HM_AVG"

        temp_df = df[["date", val_col]].copy()
        temp_df.columns = ["date", label]

        # 수치형 변환
        temp_df[label] = pd.to_numeric(temp_df[label], errors="coerce").fillna(0)

        if combined_df is None:
            combined_df = temp_df
        else:
            combined_df = pd.merge(combined_df, temp_df, on="date", how="outer")

        time.sleep(0.5)

    if combined_df is not None:
        combined_df = combined_df.sort_values("date")
        combined_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(combined_df)} rows to {OUTPUT_PATH}")
    else:
        print("No data collected.")


if __name__ == "__main__":
    collect_combined_weather()
