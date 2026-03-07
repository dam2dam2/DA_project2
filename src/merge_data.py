import pandas as pd
import os

# 경로 설정
BIKE_FILE = "/Users/dami/innercircle/DA_project2/data/daily_bike_rentals_2015_2025.csv"
WEATHER_FILE = "/Users/dami/innercircle/DA_project2/data/seoul_weather_2015_2025.csv"
OUTPUT_FILE = "/Users/dami/innercircle/DA_project2/data/bike_weather_combined.csv"


def merge_data():
    if not os.path.exists(BIKE_FILE) or not os.path.exists(WEATHER_FILE):
        print("Required files are missing.")
        return

    # 데이터 로드
    bike_df = pd.read_csv(BIKE_FILE)
    weather_df = pd.read_csv(WEATHER_FILE)

    # 날짜 형식 통일
    bike_df["date"] = pd.to_datetime(bike_df["date"]).dt.date
    weather_df["date"] = pd.to_datetime(weather_df["date"]).dt.date

    # 병합 (Inner Join 권장하나, 분석을 위해 Outer 시도 후 결측치 처리도 고려 가능)
    # 여기서는 자전거 대여 데이터가 있는 날을 기준으로 병합 (Left Join)
    combined_df = pd.merge(bike_df, weather_df, on="date", how="left")

    # 저장
    combined_df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
    print(f"Successfully merged data. Saved to {OUTPUT_FILE}")
    print(f"Total rows: {len(combined_df)}")
    print(combined_df.head())


if __name__ == "__main__":
    merge_data()
