import requests
import pandas as pd
import os
import io
import time
from datetime import datetime, timedelta

# 설정
AUTH_KEY = "oEmrXAvHS5yJq1wLx1ucSg"
STN_ID = "108"  # 서울
URL = "https://apihub.kma.go.kr/api/typ01/url/sts_ta.php"
OUTPUT_PATH = "/Users/dami/innercircle/DA_project2/data/seoul_temp_2025_nov_dec.csv"


def fetch_chunk(start_str, end_str):
    params = {
        "tm1": start_str,
        "tm2": end_str,
        "stn_id": STN_ID,
        "help": "0",
        "authKey": AUTH_KEY,
    }
    try:
        # 타임아웃 60초로 증가
        response = requests.get(URL, params=params, timeout=60)
        if response.status_code == 200:
            content = response.text
            data_lines = []
            for line in content.split("\n"):
                line = line.strip()
                if line and not line.startswith("#") and line != "=":
                    if line.endswith(",="):
                        line = line[:-2]
                    data_lines.append(line)
            return data_lines
    except Exception as e:
        print(f"Exception for {start_str}: {e}")
    return []


def collect_remaining():
    ranges = [("20251101", "20251130"), ("20251201", "20251231")]

    all_data_lines = []
    header = "YMD,STN_ID,LAT,LON,ALTD,TA_DAVG,TMX_DD,TMX_OCUR_TMA,TMN_DD,TMN_OCUR_TMA,MRNG_TMN,MRNG_TMN_OCUR_TMA,DYTM_TMX,DYTM_TMX_OCUR_TMA,NGHT_TMN,NGHT_TMN_OCUR_TMA"

    for s, e in ranges:
        print(f"Retrying {s} ~ {e}...")
        lines = fetch_chunk(s, e)
        if lines:
            all_data_lines.extend(lines)
            print(f"Got {len(lines)} lines")
        else:
            print(f"Failed to get {s}")
        time.sleep(1)

    if all_data_lines:
        csv_content = header + "\n" + "\n".join(all_data_lines)
        df = pd.read_csv(io.StringIO(csv_content))
        df["date"] = pd.to_datetime(df["YMD"], format="%Y%m%d", errors="coerce").dt.date
        df = df.dropna(subset=["date"])
        df.rename(columns={"TA_DAVG": "temp"}, inplace=True)
        result_df = df[["date", "temp"]].copy()
        result_df["temp"] = pd.to_numeric(result_df["temp"], errors="coerce").fillna(0)
        result_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Saved {len(result_df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    collect_remaining()
