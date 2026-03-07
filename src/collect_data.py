import pandas as pd
import os
import glob
import re

# 설정
DATA_DIR = "/Users/dami/innercircle/bike_data/data"
OUTPUT_PATH = (
    "/Users/dami/innercircle/DA_project2/data/daily_bike_rentals_2015_2025.csv"
)


def clean_count(val):
    if pd.isna(val):
        return 0
    if isinstance(val, str):
        # 숫자 외 문자 제거 (콤마 등)
        val = re.sub(r"[^\d]", "", val)
    try:
        return int(val)
    except:
        return 0


def process_files():
    all_data = []

    # 해당 디렉토리의 모든 csv와 xlsx 파일 목록
    files = glob.glob(os.path.join(DATA_DIR, "*"))

    for file_path in sorted(files):
        filename = os.path.basename(file_path)
        print(f"Processing: {filename}")

        try:
            if filename.endswith(".csv"):
                # 인코딩 문제 대응 (cp949, utf-8-sig 등)
                try:
                    df = pd.read_csv(file_path, encoding="cp949")
                except:
                    df = pd.read_csv(file_path, encoding="utf-8-sig")
            elif filename.endswith(".xlsx"):
                df = pd.read_excel(file_path)
            else:
                continue

            # 컬럼명 정규화 (대여일자, 대여일, 일자 등 -> date / 대여건수, 대여수 등 -> count)
            # 파일마다 컬럼명이 다를 수 있으므로 키워드 매칭
            date_col = None
            count_col = None

            for col in df.columns:
                if "일자" in col or "일" in str(col) or "Date" in str(col):
                    if "대여" in col or col == "일자" or col == "기준일":
                        date_col = col
                if "건수" in col or "수" in str(col) or "Count" in str(col):
                    if "대여" in col or "건수" in col:
                        count_col = col

            # 특정 파일 예외 처리 (대여소별 데이터 등은 일별 합계가 필요할 수 있음)
            if "대여소별" in filename:
                # 대여소별 데이터는 보통 대여일자, 대여소번호, 대여소명, 대여건수 구조
                # 일별 합계로 group by
                if date_col and count_col:
                    temp_df = df[[date_col, count_col]].copy()
                    temp_df.columns = ["date", "count"]
                    temp_df["count"] = temp_df["count"].apply(clean_count)
                    # 날짜 형식 변환 시도
                    temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
                    temp_df = temp_df.dropna(subset=["date"])
                    daily_sum = temp_df.groupby("date")["count"].sum().reset_index()
                    all_data.append(daily_sum)
            else:
                if date_col and count_col:
                    temp_df = df[[date_col, count_col]].copy()
                    temp_df.columns = ["date", "count"]
                    temp_df["count"] = temp_df["count"].apply(clean_count)
                    temp_df["date"] = pd.to_datetime(temp_df["date"], errors="coerce")
                    temp_df = temp_df.dropna(subset=["date"])
                    all_data.append(temp_df)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        # 중복 날짜 처리 (여러 파일에 걸쳐 있는 경우 합산)
        final_df = final_df.groupby("date")["count"].sum().sort_index().reset_index()

        # 2015년부터 2025년까지 필터링 (필요시)
        final_df = final_df[
            (final_df["date"].dt.year >= 2015) & (final_df["date"].dt.year <= 2025)
        ]

        final_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
        print(f"Successfully saved {len(final_df)} rows to {OUTPUT_PATH}")
    else:
        print("No data collected.")


if __name__ == "__main__":
    process_files()
