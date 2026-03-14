import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
import glob
import re
import numpy as np

# 설정
pd.set_option("display.max_columns", None)
SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)


def clean_and_float(s):
    if s is None or pd.isna(s):
        return 0.0
    if isinstance(s, str):
        s = s.replace(",", "").replace(" ", "")
        if s == "" or s == "-" or s == "null":
            return 0.0
        try:
            return float(s)
        except:
            return 0.0
    return float(s)


def load_all_data():
    """모든 데이터 파일을 사전 로드 및 기본 전처리"""
    data_dict = {}

    # 1. 인천공항 기본 (2002-2025)
    try:
        f = pd.read_csv("data/airport_flights_2002_2025.csv")
        p = pd.read_csv("data/airport_passengers_2002_2025.csv")
        c = pd.read_csv("data/airport_cargo_2002_2025.csv")

        p["passenger"] = p["passenger"].astype(str).apply(clean_and_float)
        p["arrPassenger"] = p["arrPassenger"].astype(str).apply(clean_and_float)
        p["depPassenger"] = p["depPassenger"].astype(str).apply(clean_and_float)
        c["baggage"] = c["baggage"].astype(str).apply(clean_and_float)
        f["flight"] = f["flight"].astype(str).apply(clean_and_float)

        m = pd.merge(f, p, on=["year", "time"])
        m = pd.merge(m, c, on=["year", "time"])
        data_dict["airport_base"] = m
    except:
        pass

    # 2. Airportal 상세 (2018-2025)
    detail_files = glob.glob("data/airportal_detail_*.csv")
    details = []
    for f in detail_files:
        fn = os.path.basename(f)
        match = re.search(r"detail_(.*)_(.*)_(.*)_2018_2025", fn)
        if match:
            df = pd.read_csv(f)
            df["sched_type"] = match.group(1)
            df["pax_type"] = match.group(2)
            df["dir_type"] = match.group(3)
            df["pass"] = df["pass"].astype(str).apply(clean_and_float)
            df["flight_cnt"] = df["flight_cnt"].astype(str).apply(clean_and_float)
            details.append(df)
    if details:
        data_dict["airportal_detail"] = pd.concat(details, ignore_index=True)

    # 3. KOSIS & Weather
    kosis_mapping = {
        "kosis_day": "data/kosis_요일별_2005_2025.csv",
        "kosis_delay": "data/kosis_지연별_2005_2025.csv",
        "kosis_cancel": "data/kosis_결항별_2005_2025.csv",
        "kosis_airport": "data/kosis_공항별_2005_2025.csv",
        "kosis_airline": "data/kosis_항공사별_2005_2025.csv",
        "kosis_region": "data/kosis_국제선_지역별_2005_2025.csv",
    }
    for k, v in kosis_mapping.items():
        if os.path.exists(v):
            df = pd.read_csv(v)
            df["DT"] = df["DT"].astype(str).apply(clean_and_float)
            data_dict[k] = df

    if os.path.exists("data/seoul_weather_2015_2025.csv"):
        data_dict["weather"] = pd.read_csv("data/seoul_weather_2015_2025.csv")

    # 4. Route
    try:
        data_dict["route_intl"] = pd.read_csv(
            "data/airportal_route_international_2018_2025.csv"
        )
        data_dict["route_dom"] = pd.read_csv(
            "data/airportal_route_domestic_2018_2025.csv"
        )
        for k in ["route_intl", "route_dom"]:
            data_dict[k]["total_PERSON"] = (
                data_dict[k]["total_PERSON"].astype(str).apply(clean_and_float)
            )
    except:
        pass

    return data_dict


def run_25_eda(data):
    print(">>> 25가지 EDA 시각화 생성 중...")

    # --- 탭 1: 장기 트렌드 분석 (1-3) ---
    if "airport_base" in data:
        base = data["airport_base"]
        yearly = (
            base.groupby("year")[["flight", "passenger", "baggage"]].sum().reset_index()
        )
        # 1. 연도별 여객
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=yearly, x="year", y="passenger", marker="o", linewidth=2)
        plt.title("1. 연도별 총 여객 추이 (2002-2025)")
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{SAVE_DIR}/01_yearly_pax.png")
        plt.close()
        # 2. 연도별 운항
        plt.figure(figsize=(12, 6))
        sns.lineplot(
            data=yearly, x="year", y="flight", marker="s", color="orange", linewidth=2
        )
        plt.title("2. 연도별 총 운항 추이 (2002-2025)")
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{SAVE_DIR}/02_yearly_flight.png")
        plt.close()
        # 3. 연도별 화물
        plt.figure(figsize=(12, 6))
        sns.lineplot(
            data=yearly, x="year", y="baggage", marker="^", color="green", linewidth=2
        )
        plt.title("3. 연도별 총 화물 추이 (2002-2025)")
        plt.grid(True, alpha=0.3)
        plt.savefig(f"{SAVE_DIR}/03_yearly_cargo.png")
        plt.close()

    # --- 탭 2: 수요 패턴 및 계절성 (4-7) ---
    if "airportal_detail" in data:
        # 4. 월별 여객 계절성
        monthly = data["airportal_detail"].groupby("month")["pass"].sum().reset_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(data=monthly, x="month", y="pass", palette="coolwarm")
        plt.title("4. 월별 여객 수요 계절성 분포")
        plt.savefig(f"{SAVE_DIR}/04_monthly_season.png")
        plt.close()

    if "kosis_day" in data:
        # 5. 요일별 운송량
        df = data["kosis_day"]
        labels = "C1_NM" if "C1_NM" in df.columns else "C2_NM"
        day_sum = (
            df[~df[labels].isin(["합계", "계"])]
            .groupby(labels)["DT"]
            .sum()
            .reset_index()
        )
        plt.figure(figsize=(12, 6))
        sns.barplot(data=day_sum, x=labels, y="DT", palette="Set2")
        plt.title("5. 요일별 평균 운임량 분석")
        plt.savefig(f"{SAVE_DIR}/05_day_dist.png")
        plt.close()

    if "airport_base" in data:
        hourly = (
            data["airport_base"]
            .groupby("time")[["passenger", "flight"]]
            .mean()
            .reset_index()
        )
        # 6. 시간대별 여객 피크
        plt.figure(figsize=(14, 6))
        sns.pointplot(data=hourly, x="time", y="passenger", color="blue")
        plt.xticks(rotation=45)
        plt.title("6. 시간대별 평균 여객 수요 피크 분석")
        plt.savefig(f"{SAVE_DIR}/06_hourly_pax.png")
        plt.close()
        # 7. 시간대별 운항 피크
        plt.figure(figsize=(14, 6))
        sns.pointplot(data=hourly, x="time", y="flight", color="red")
        plt.xticks(rotation=45)
        plt.title("7. 시간대별 평균 운항 슬롯 점유 패턴")
        plt.savefig(f"{SAVE_DIR}/07_hourly_flight.png")
        plt.close()

    # --- 탭 3: 여객 및 운송 특성 (8-12) ---
    if "airportal_detail" in data:
        det = data["airportal_detail"]
        # 8. 정기 vs 부정기
        sched = det.groupby("sched_type")["pass"].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(
            sched, labels=sched.index, autopct="%1.1f%%", explode=[0.05, 0], shadow=True
        )
        plt.title("8. 운항 성격별 여객 비중 (정기 vs 부정기)")
        plt.savefig(f"{SAVE_DIR}/08_sched_pie.png")
        plt.close()
        # 9. 유임 vs 환승
        ptype = det.groupby("pax_type")["pass"].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(
            ptype,
            labels=ptype.index,
            autopct="%1.1f%%",
            colors=["#ff9999", "#66b3ff"],
            pctdistance=0.85,
        )
        plt.title("9. 여객 유형별 비중 (유임 vs 환승)")
        plt.savefig(f"{SAVE_DIR}/09_pax_type_pie.png")
        plt.close()
        # 10. 출발 vs 도착
        direc = det.groupby("dir_type")["pass"].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(
            direc, labels=direc.index, autopct="%1.1f%%", colors=["lightgreen", "gold"]
        )
        plt.title("10. 공항 이용 방향별 여객 균형 (출발 vs 도착)")
        plt.savefig(f"{SAVE_DIR}/10_direction_pie.png")
        plt.close()

    if "route_intl" in data and "route_dom" in data:
        # 11. 국내 vs 국제 여객 비중
        intl_pax = data["route_intl"]["total_PERSON"].sum()
        dom_pax = data["route_dom"]["total_PERSON"].sum()
        plt.figure(figsize=(8, 8))
        plt.pie(
            [dom_pax, intl_pax],
            labels=["Domestic", "International"],
            autopct="%1.1f%%",
            colors=["lightskyblue", "lightcoral"],
        )
        plt.title("11. 국내선 대비 국제선 여객 운송 비중 (2018-2025)")
        plt.savefig(f"{SAVE_DIR}/11_dom_intl_ratio.png")
        plt.close()
        # 12. 주요 거점 공항별 분담률
        if "kosis_airport" in data:
            dfa = data["kosis_airport"]
            al = "C1_NM" if "C1_NM" in dfa.columns else "C1_OBJ_NM"
            major = (
                dfa[dfa[al].isin(["인천", "김포", "제주", "김해"])]
                .groupby(al)["DT"]
                .sum()
            )
            plt.figure(figsize=(8, 8))
            plt.pie(major, labels=major.index, autopct="%1.1f%%")
            plt.title("12. 주요 거점 공항별 여객 분담률")
            plt.savefig(f"{SAVE_DIR}/12_airport_share.png")
            plt.close()

    # --- 탭 4: 노선 및 시장 점유율 (13-17) ---
    if "kosis_region" in data:
        # 13. 국제선 지역별 수요 (아시아, 유럽 등)
        df = data["kosis_region"]
        al = "C1_NM" if "C1_NM" in df.columns else "C1_OBJ_NM"
        reg = (
            df[~df[al].isin(["합계", "계", "항공사별", "공항별"])]
            .groupby(al)["DT"]
            .sum()
            .nlargest(10)
        )
        plt.figure(figsize=(12, 7))
        sns.barplot(x=reg.values, y=reg.index, palette="magma")
        plt.title("13. 국제선 주요 지역별 여객 수요 분포")
        plt.savefig(f"{SAVE_DIR}/13_intl_region.png")
        plt.close()

    if "route_intl" in data:
        # 14. 상위 15개 국제 노선 (공항별)
        top15i = (
            data["route_intl"]
            .groupby("ap2")["total_PERSON"]
            .sum()
            .nlargest(15)
            .reset_index()
        )
        plt.figure(figsize=(12, 9))
        sns.barplot(data=top15i, x="total_PERSON", y="ap2", color="skyblue")
        plt.title("14. 상위 15개 국제 핵심 노선 성과")
        plt.savefig(f"{SAVE_DIR}/14_top15_intl.png")
        plt.close()
        # 15. 연도별 국제선 여객 성장률
        gi = data["route_intl"].groupby("year")["total_PERSON"].sum().pct_change() * 100
        plt.figure(figsize=(12, 6))
        plt.plot(gi.index, gi.values, marker="o", color="purple")
        plt.title("15. 국제선 여객 연간 성장률 추이(%)")
        plt.savefig(f"{SAVE_DIR}/15_intl_growth.png")
        plt.close()

    if "route_dom" in data:
        # 16. 상위 10개 국내 핵심 노선 (제주 등)
        top10d = (
            data["route_dom"]
            .groupby("ap2")["total_PERSON"]
            .sum()
            .nlargest(10)
            .reset_index()
        )
        plt.figure(figsize=(12, 6))
        sns.barplot(data=top10d, x="total_PERSON", y="ap2", palette="YlOrRd")
        plt.title("16. 상위 10개 국내 핵심 노선 성과")
        plt.savefig(f"{SAVE_DIR}/16_top10_dom.png")
        plt.close()

    if "kosis_airline" in data:
        # 17. 주요 항공사별 시장 점유율
        df = data["kosis_airline"]
        al = "C1_NM" if "C1_NM" in df.columns else "C1_OBJ_NM"
        top_a = (
            df[~df[al].isin(["합계", "계", "항공사별"])]
            .groupby(al)["DT"]
            .sum()
            .nlargest(12)
        )
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_a.values, y=top_a.index, palette="viridis")
        plt.title("17. 주요 항공사별 시장 점유율 및 성과")
        plt.savefig(f"{SAVE_DIR}/17_airline_share.png")
        plt.close()

    # --- 탭 5: 정시성 및 장애 (18-21) ---
    if "kosis_delay" in data:
        # 18. 연도별 항공기 지연 발생 빈도
        d = data["kosis_delay"]
        d["year"] = d["PRD_DE"].astype(str).str[:4]
        y_delay = d.groupby("year")["DT"].sum().reset_index()
        plt.figure(figsize=(12, 6))
        sns.lineplot(data=y_delay, x="year", y="DT", marker="o", color="red")
        plt.title("18. 연도별 항공기 지연(Delay) 발생 빈도 추이")
        plt.savefig(f"{SAVE_DIR}/18_delay_trend.png")
        plt.close()
        # 19. 월별 평균 지연 집중도
        d["month"] = d["PRD_DE"].astype(str).str[4:6]
        m_delay = d.groupby("month")["DT"].mean().reset_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(data=m_delay, x="month", y="DT", palette="Reds")
        plt.title("19. 월별 평균 항공기 지연 집중도 분석")
        plt.savefig(f"{SAVE_DIR}/19_monthly_delay.png")
        plt.close()

    if "kosis_cancel" in data:
        # 20. 연도별 항공기 결항 발생 빈도
        c = data["kosis_cancel"]
        c["year"] = c["PRD_DE"].astype(str).str[:4]
        y_cancel = c.groupby("year")["DT"].sum().reset_index()
        plt.figure(figsize=(12, 6))
        sns.barplot(data=y_cancel, x="year", y="DT", color="darkred")
        plt.title("20. 연도별 항공기 결항(Cancellation) 발생 빈도 추이")
        plt.savefig(f"{SAVE_DIR}/20_cancel_trend.png")
        plt.close()
    if "kosis_delay" in data and "kosis_cancel" in data:
        # 21. 공항별 지연 vs 결항 상관성
        d = data["kosis_delay"]
        c = data["kosis_cancel"]
        al_col = "C1_NM" if "C1_NM" in d.columns else "C1_OBJ_NM"
        d_sum = (
            d[~d[al_col].isin(["합계", "계"])].groupby(al_col)["DT"].sum().reset_index()
        )
        c_sum = (
            c[~c[al_col].isin(["합계", "계"])].groupby(al_col)["DT"].sum().reset_index()
        )
        m = pd.merge(d_sum, c_sum, on=al_col, suffixes=("_delay", "_cancel"))
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=m, x="DT_delay", y="DT_cancel", hue=al_col, s=100)
        plt.title("21. 공항별 지연 및 결항 건수 상관관계")
        plt.savefig(f"{SAVE_DIR}/21_delay_cancel_corr.png")
        plt.close()

    # --- 탭 6: 기상 복합 분석 (22-25) ---
    if "weather" in data and "kosis_cancel" in data:
        w = data["weather"]
        w["PRD_DE"] = pd.to_datetime(w["date"]).dt.strftime("%Y%m").astype(int)
        mw = (
            w.groupby("PRD_DE")
            .agg(
                {
                    "precip": "sum",
                    "wind_speed": "mean",
                    "temp": "mean",
                    "humidity": "mean",
                }
            )
            .reset_index()
        )
        mc = data["kosis_cancel"].groupby("PRD_DE")["DT"].sum().reset_index()
        m = pd.merge(mw, mc, on="PRD_DE")

        # 22. 기상 요인-결항 상관계수 히트맵
        plt.figure(figsize=(10, 8))
        sns.heatmap(
            m[["precip", "wind_speed", "temp", "humidity", "DT"]].corr(),
            annot=True,
            cmap="RdBu_r",
            fmt=".2f",
        )
        plt.title("22. 기상 요인과 결항 건수의 상관분석 히트맵")
        plt.savefig(f"{SAVE_DIR}/22_weather_heatmap.png")
        plt.close()
        # 23. 풍속 영향에 따른 결항 산점도
        plt.figure(figsize=(12, 7))
        sns.regplot(
            data=m,
            x="wind_speed",
            y="DT",
            scatter_kws={"alpha": 0.6},
            line_kws={"color": "red"},
        )
        plt.title("23. 평균 풍속과 결항 건수의 통계적 상관관계")
        plt.savefig(f"{SAVE_DIR}/23_wind_reg.png")
        plt.close()
        # 24. 강수량과 결항의 버블 차트
        plt.figure(figsize=(12, 7))
        plt.scatter(
            m["precip"],
            m["DT"],
            s=m["wind_speed"] * 50,
            alpha=0.5,
            c=m["temp"],
            cmap="viridis",
        )
        plt.colorbar(label="Temperature (°C)")
        plt.xlabel("Monthly Precipitation (mm)")
        plt.ylabel("Cancellations")
        plt.title("24. 강수량 및 풍속 복합 영향 분석 (Color: 기온)")
        plt.savefig(f"{SAVE_DIR}/24_precip_bubble.png")
        plt.close()
        # 25. 계절별 결항 발생 편차 분석
        m["month"] = (m["PRD_DE"] % 100).astype(int)
        plt.figure(figsize=(12, 7))
        sns.boxplot(data=m, x="month", y="DT", palette="Set3")
        plt.title("25. 월별 결항 발생 편차 및 계절적 특성")
        plt.savefig(f"{SAVE_DIR}/25_seasonal_variation.png")
        plt.close()

    print(f">>> 25가지 심층 분석 시각화 완료! ( {SAVE_DIR}/ 폴더 확인 )")


if __name__ == "__main__":
    all_data = load_all_data()
    run_25_eda(all_data)
