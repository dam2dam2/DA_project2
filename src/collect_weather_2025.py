import requests
import pandas as pd
import os
import io
import time
from datetime import datetime, timedelta

# 설정
AUTH_KEY = "oEmrXAvHS5yJq1wLx1ucSg"
STN_ID = "108"  # 서울 (사용자 URL의 0은 모든 지점이나, 분석 효율을 위해 서울 권장. 필요시 0으로 변경 가능)
URL = "https://apihub.kma.go.kr/api/typ01/url/sts_ta.php"
OUTPUT_PATH = "/Users/dami/innercircle/DA_project2/data/seoul_temp_2025.csv"


def fetch_chunk(start_str, end_str):
    params = {
        "tm1": start_str,
        "tm2": end_str,
        "stn_id": STN_ID,
        "help": "0",
        "authKey": AUTH_KEY,
    }
    try:
        response = requests.get(URL, params=params, timeout=30)
        if response.status_code == 200:
            content = response.text
            # 데이터 라인만 추출 (주석 # 및 구분자 = 제외)
            data_lines = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and line != "=":
                    # 줄 끝의 ,= 제거
                    if line.endswith(",="):
                        line = line[:-2]
                    data_lines.append(line)
            return data_lines
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return []


def collect_2025_temp_remaining():
    # 누락된 2025년 10월 28일부터 12월 31일까지 추출
    start_date = datetime(2025, 10, 28)
    end_date = datetime(2025, 12, 31)

    # 현재 날짜까지만 제한 (미래 데이터 방지)
    now = datetime.now()
    if end_date > now:
        end_date = now

    current_dt = start_date
    delta = timedelta(days=29)  # 30일 이내 권장

    all_data_lines = []

    # 헤더 정의 (sts_ta.php 기준 16개 컬럼)
    header = "YMD,STN_ID,LAT,LON,ALTD,TA_DAVG,TMX_DD,TMX_OCUR_TMA,TMN_DD,TMN_OCUR_TMA,MRNG_TMN,MRNG_TMN_OCUR_TMA,DYTM_TMX,DYTM_TMX_OCUR_TMA,NGHT_TMN,NGHT_TMN_OCUR_TMA"

    print(f"Starting data collection from {start_date.date()} to {end_date.date()}...")

    while current_dt <= end_date:
        next_dt = min(current_dt + delta, end_date)
        s_str = current_dt.strftime("%Y%m%d")
        e_str = next_dt.strftime("%Y%m%d")

        print(f"Fetching {s_str} ~ {e_str}...")
        lines = fetch_chunk(s_str, e_str)
        all_data_lines.extend(lines)

        current_dt = next_dt + timedelta(days=1)
        time.sleep(0.3)

    if all_data_lines:
        csv_content = header + "\n" + "\n".join(all_data_lines)
        df = pd.read_csv(io.StringIO(csv_content))

        # 데이터 정제
        df["date"] = pd.to_datetime(df["YMD"], format="%Y%m%d", errors="coerce").dt.date
        df = df.dropna(subset=["date"])  # 파싱 오류로 생긴 더미 행 제거

        df.rename(columns={"TA_DAVG": "temp"}, inplace=True)

        result_df = df[["date", "temp"]].copy()
        result_df["temp"] = pd.to_numeric(result_df["temp"], errors="coerce").fillna(0)

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        result_df.to_csv(
            OUTPUT_PATH.replace(".csv", "_remaining.csv"),
            index=False,
            encoding="utf-8-sig",
        )
        print(
            f"Stored {len(result_df)} rows in {OUTPUT_PATH.replace('.csv', '_remaining.csv')}"
        )


if __name__ == "__main__":
    collect_2025_temp_remaining()
