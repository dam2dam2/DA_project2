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

    # 4. Route (기존 및 상세 노선 데이터 통합)
    try:
        # 기존 요약 데이터
        data_dict["route_intl_sum"] = pd.read_csv(
            "data/airportal_route_international_2018_2025.csv"
        )
        data_dict["route_dom_sum"] = pd.read_csv(
            "data/airportal_route_domestic_2018_2025.csv"
        )

        # 신규 수집된 상세 데이터 (노선별)
        detailed_route_path = "data/airportal_route_intl_detailed_2018_2025.csv"
        if os.path.exists(detailed_route_path):
            df_route = pd.read_csv(detailed_route_path)
            for col in ["pass", "cargo", "flight_cnt"]:
                if col in df_route.columns:
                    df_route[col] = df_route[col].astype(str).apply(clean_and_float)
            df_route["year"] = df_route["year_month"].astype(str).str[:4].astype(int)
            df_route["month"] = df_route["year_month"].astype(str).str[4:6].astype(int)
            data_dict["route_intl_detailed"] = df_route

        for k in ["route_intl_sum", "route_dom_sum"]:
            if k in data_dict:
                data_dict[k]["total_PERSON"] = (
                    data_dict[k]["total_PERSON"].astype(str).apply(clean_and_float)
                )
    except Exception as e:
        print(f"데이터 로드 에러 (Route): {e}")

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

    # --- 탭 7: 국제 노선별 상세 분석 (26-30) [NEW] ---
    if "route_intl_detailed" in data:
        print(">>> 국제 노선 상세 분석 중 (26-30)...")
        df_det = data["route_intl_detailed"]

        # 26. 상위 15개 국제 노선 (인천공항 상세)
        top15_det = (
            df_det.groupby("airport_name")["pass"].sum().nlargest(15).reset_index()
        )
        plt.figure(figsize=(12, 8))
        sns.barplot(data=top15_det, x="pass", y="airport_name", palette="rocket")
        plt.title("26. 인천공항 기반 상위 15개 국제 핵심 노선 (2018-2025)")
        plt.xlabel("누적 여객 수 (명)")
        plt.ylabel("도착지 공항")
        plt.savefig(f"{SAVE_DIR}/26_top15_intl_det.png")
        plt.close()

        # 27. 주요 국제 노선 여객 추이 (정상 운영 기간 모든 월 1만 명 이상 노선 중 상/하위 3개 강조)
        # 1) 데이터 결측치 및 팬데믹 기간 제외 (정상 운영 월 정의)
        # 월별 총 여객이 0이거나 극소수(단위 오류 등)인 달은 수집 누락으로 판단하여 필터링 대상에서 제외
        monthly_total_pass = df_det.groupby("year_month")["pass"].sum()
        valid_months = monthly_total_pass[
            monthly_total_pass > 100000
        ].index.tolist()  # 월 10만명 미만은 비정상 기간으로 간주

        # 2) 코로나19 기간(2020-2022) 추가 제외
        df_det["ym_int"] = df_det["year_month"].astype(int)
        df_normal_period = df_det[df_det["year_month"].isin(valid_months)]
        df_normal_period = df_normal_period[
            (df_normal_period["ym_int"] < 202001)
            | (df_normal_period["ym_int"] > 202212)
        ]

        # 3) '정상 운영 기간' 중 모든 월 10,000명 이상 유지 노선 식별
        min_pass_normal = df_normal_period.groupby("airport_name")["pass"].min()
        target_airports = min_pass_normal[min_pass_normal >= 10000].index.tolist()

        print(f"   - 필터링 통과한 진정 핵심 노선 수: {len(target_airports)}개")

        # 배경용 (월 최대 1만명 넘었으나 타겟 제외)
        max_pass_all = df_det.groupby("airport_name")["pass"].max()
        bg_airports = max_pass_all[
            (max_pass_all >= 10000) & (~max_pass_all.index.isin(target_airports))
        ].index.tolist()

        plt.figure(figsize=(15, 8))
        all_trend = df_det.groupby(["year", "airport_name"])["pass"].sum().reset_index()

        # 배경 노선 (연한 회색)
        for node in bg_airports:
            node_data = all_trend[all_trend["airport_name"] == node]
            plt.plot(
                node_data["year"],
                node_data["pass"],
                color="#E0E0E0",
                alpha=0.1,
                linewidth=0.5,
            )

        if target_airports:
            # 4) 타겟 노선 중 누적 실적 기준 상/하위 3개 선정
            agg_pass_target = (
                df_det[df_det["airport_name"].isin(target_airports)]
                .groupby("airport_name")["pass"]
                .sum()
                .sort_values(ascending=False)
            )
            top3 = agg_pass_target.head(3).index.tolist()
            bottom3 = agg_pass_target.tail(3).index.tolist()

            # 5) 시각화 및 강조
            for node in target_airports:
                node_data = all_trend[all_trend["airport_name"] == node]
                if node in top3:
                    color = "#D00000"
                    linewidth = 4
                    label = f"TOP: {node}"
                    zorder = 10
                elif node in bottom3:
                    color = "#1A75FF"
                    linewidth = 3
                    label = f"BOTTOM: {node}"
                    zorder = 9
                else:
                    color = "#2D6A4F"
                    linewidth = 1.5
                    label = None
                    zorder = 5  # 수많은 노선이므로 범례 생략

                plt.plot(
                    node_data["year"],
                    node_data["pass"],
                    color=color,
                    linewidth=linewidth,
                    marker="o" if node in top3 + bottom3 else None,
                    label=label,
                    zorder=zorder,
                )

            plt.legend(
                title="핵심 분석 노선 (상/하위 3개)",
                bbox_to_anchor=(1.05, 1),
                loc="upper left",
            )

        plt.title(
            "27. 주요 국제 노선 여객 추이 (정상 월 1만명 이상 유지 노선 상/하위 강조)"
        )
        plt.xlabel("연도")
        plt.ylabel("연간 누적 여객 수 (명)")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{SAVE_DIR}/27_top5_route_trend.png")
        plt.close()
        print(f">>> 27번 시각화 완료 (분석 대상: {len(target_airports)}개)")

        # 28. 코로나19 전후 노선별 회복 탄력성 분석 (2019 vs 2024)
        recovery = (
            df_det[df_det["year"].isin([2019, 2024])]
            .groupby(["year", "airport_name"])["pass"]
            .sum()
            .unstack(level=0)
        )
        recovery["recovery_rate"] = (recovery[2024] / recovery[2019]) * 100
        top_rec = (
            recovery.dropna().sort_values("recovery_rate", ascending=False).head(15)
        )
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_rec["recovery_rate"], y=top_rec.index, palette="viridis")
        plt.axvline(100, color="red", linestyle="--")
        plt.title("28. 주요 노선별 코로나19 이전(2019) 대비 회복률 (2024)")
        plt.xlabel("회복률 (%) - 100% 이상은 2019년 추월")
        plt.savefig(f"{SAVE_DIR}/28_route_recovery.png")
        plt.close()

        # 29. 주요 노선별 화물 vs 여객 비중 (전략적 노선 분류)
        route_attr = (
            df_det.groupby("airport_name")[["pass", "cargo"]].sum().reset_index()
        )
        route_attr = route_attr[
            route_attr["pass"] > route_attr["pass"].quantile(0.7)
        ]  # 상위 노선 대상
        plt.figure(figsize=(12, 8))
        plt.scatter(
            route_attr["pass"], route_attr["cargo"], alpha=0.6, s=100, c="coral"
        )
        for i, txt in enumerate(route_attr["airport_name"]):
            if i % 5 == 0:  # 텍스트 겹침 방지
                plt.annotate(
                    txt,
                    (route_attr["pass"].iloc[i], route_attr["cargo"].iloc[i]),
                    fontsize=9,
                )
        plt.title("29. 노선별 여객-화물 복합 특성 분석 (포지셔닝)")
        plt.xlabel("누적 여객 수")
        plt.ylabel("누적 화물량")
        plt.savefig(f"{SAVE_DIR}/29_route_pax_cargo.png")
        plt.close()

        # 30. 노선별 편당 평균 여객 수 (운항 효율성 지표)
        df_det["efficiency"] = df_det["pass"] / df_det["flight_cnt"].replace(0, np.nan)
        eff_rank = df_det.groupby("airport_name")["efficiency"].mean().nlargest(15)
        plt.figure(figsize=(12, 8))
        sns.barplot(x=eff_rank.values, y=eff_rank.index, palette="coolwarm")
        plt.title("30. 노선별 편당 평균 여객 수 (운항 효율성 지표)")
        plt.xlabel("편당 여객 수 (명)")
        plt.savefig(f"{SAVE_DIR}/30_route_efficiency.png")
        plt.close()

        # --- 31~36. 주요 지역별 심층 추이 및 통합 비교 (사용자 요청 추가) ---

        # 1) 지역 분류 매핑 정의
        region_map = {
            "Japan": {
                "kw": [
                    "나리타",
                    "HND",
                    "하네다",
                    "KIX",
                    "간사이",
                    "FUK",
                    "후쿠오카",
                    "NGO",
                    "나고야",
                    "CTS",
                    "삿보로",
                    "OKA",
                    "오끼나와",
                    "UKB",
                    "고베",
                    "KMQ",
                    "고마스",
                    "NGS",
                    "나가사키",
                    "KIJ",
                    "니이가타",
                    "MYJ",
                    "마즈야마",
                    "SDJ",
                    "센다이",
                    "TAK",
                    "다가마스",
                    "OKJ",
                    "오까야마",
                    "KOJ",
                    "카고시마",
                    "KKJ",
                    "키타큐슈",
                ],
                "color": "Reds",
                "main": "#D00000",
                "name": "일본",
            },
            "Europe": {
                "kw": [
                    "LHR",
                    "히드로",
                    "CDG",
                    "샤를드골",
                    "FRA",
                    "프랑크푸르트",
                    "FCO",
                    "로마",
                    "MUC",
                    "뮌헨",
                    "AMS",
                    "암스텔담",
                    "IST",
                    "이스탄불",
                    "PRG",
                    "프라하",
                    "MAD",
                    "마드리드",
                    "ZRH",
                    "취리히",
                    "VIE",
                    "비엔나",
                    "CPH",
                    "코펜하겐",
                    "BCN",
                    "바르셀로나",
                    "HEL",
                    "헬싱키",
                    "WAW",
                    "바르샤바",
                    "BUD",
                    "부다페스트",
                    "MXP",
                    "밀라노",
                    "VCE",
                    "베니스",
                ],
                "color": "Blues",
                "main": "#1A75FF",
                "name": "유럽",
            },
            "China": {
                "kw": [
                    "PEK",
                    "북경",
                    "PVG",
                    "푸동",
                    "PKX",
                    "다싱",
                    "CAN",
                    "광저우",
                    "TAO",
                    "청도",
                    "TSN",
                    "천진",
                    "SHA",
                    "상해",
                    "DLC",
                    "대련",
                    "SHE",
                    "심양",
                    "SZX",
                    "심천",
                    "CGO",
                    "정저우",
                    "CSX",
                    "창사",
                    "CTU",
                    "청두",
                    "CKG",
                    "총킹",
                    "XMN",
                    "샤먼",
                    "YAS",
                    "연길",
                    "YNT",
                    "연대",
                    "WEH",
                    "웨이하이",
                    "YNJ",
                    "연길",
                ],
                "color": "Oranges",
                "main": "#FF8C00",
                "name": "중국",
            },
            "Korea": {
                "kw": [
                    "PUS",
                    "김해",
                    "CJU",
                    "제주",
                    "TAE",
                    "대구",
                    "KWJ",
                    "광주",
                    "CJJ",
                    "청주",
                    "YNY",
                    "양양",
                ],
                "color": "Purples",
                "main": "#8A2BE2",
                "name": "한국(내항기)",
            },
            "SEA": {
                "kw": [
                    "BKK",
                    "방콕",
                    "DMK",
                    "돈무앙",
                    "DAD",
                    "다낭",
                    "HAN",
                    "하노이",
                    "SGN",
                    "호치민",
                    "MNL",
                    "마닐라",
                    "CEB",
                    "세부",
                    "SIN",
                    "싱가폴",
                    "HKT",
                    "푸켓",
                    "KUL",
                    "쿠알라룸푸르",
                    "PQC",
                    "푸쿡",
                    "CXR",
                    "나트랑",
                    "DLI",
                    "달랏",
                    "VCA",
                    "껀터",
                    "KLO",
                    "칼리보",
                    "PPS",
                    "프에르토",
                ],
                "color": "Greens",
                "main": "#2D6A4F",
                "name": "동남아",
            },
        }

        # 지역 할당 함수
        def assign_region(name):
            for r, info in region_map.items():
                if any(kw in str(name) for kw in info["kw"]):
                    return r
            return "Other"

        df_det["region"] = df_det["airport_name"].apply(assign_region)

        # 2) 31-35. 지역별 개별 노선 추이 (전용 컬러 테마)
        monthly_total_pass = df_det.groupby("year_month")["pass"].sum()
        valid_months = monthly_total_pass[monthly_total_pass > 100000].index.tolist()
        df_det["ym_int"] = df_det["year_month"].astype(int)
        df_normal = df_det[df_det["year_month"].isin(valid_months)]
        df_normal = df_normal[
            (df_normal["ym_int"] < 202001) | (df_normal["ym_int"] > 202212)
        ]

        plot_idx = 31
        for r, info in region_map.items():
            df_r = df_det[df_det["region"] == r]
            df_r_normal = df_normal[df_normal["region"] == r]

            # 우량 노선 선별 (정상 기간 월 1만명+)
            min_pass_r = df_r_normal.groupby("airport_name")["pass"].min()
            targets_r = min_pass_r[min_pass_r >= 10000].index.tolist()

            # 배경 노선
            bg_r = df_r[~df_r["airport_name"].isin(targets_r)]["airport_name"].unique()

            plt.figure(figsize=(14, 7))
            all_r_trend = (
                df_r.groupby(["year", "airport_name"])["pass"].sum().reset_index()
            )

            # 배경
            for node in bg_r:
                node_data = all_r_trend[all_r_trend["airport_name"] == node]
                plt.plot(
                    node_data["year"],
                    node_data["pass"],
                    color="#E0E0E0",
                    alpha=0.15,
                    linewidth=0.5,
                )

            # 타겟 (전용 컬러맵)
            if targets_r:
                colors = sns.color_palette(info["color"], n_colors=len(targets_r))
                for i, node in enumerate(targets_r):
                    node_data = all_r_trend[all_r_trend["airport_name"] == node]
                    plt.plot(
                        node_data["year"],
                        node_data["pass"],
                        color=colors[i],
                        linewidth=2.5,
                        marker="o",
                        label=node,
                        alpha=0.8,
                    )

                plt.legend(
                    title=f"{info['name']} 핵심 노선",
                    bbox_to_anchor=(1.05, 1),
                    loc="upper left",
                    fontsize=9,
                )

            plt.title(
                f"{plot_idx}. {info['name']} 지역 우량 노선 여객 추이 (정상 월 1만+) - {info['color']} 테마"
            )
            plt.xlabel("연도")
            plt.ylabel("연간 여객 수 (명)")
            plt.grid(True, linestyle="--", alpha=0.3)
            plt.tight_layout()
            plt.savefig(f"{SAVE_DIR}/{plot_idx}_route_{r.lower()}.png")
            plt.close()
            print(
                f">>> {plot_idx}번 ({info['name']}) 시각화 완료 (타겟: {len(targets_r)}개)"
            )
            plot_idx += 1

        # 3) 36. 지역별 합계 통합 비교 시각화 (각 그룹별 추이 비교)
        plt.figure(figsize=(15, 8))
        region_yearly = df_det.groupby(["year", "region"])["pass"].sum().reset_index()
        # 'Other' 제외하고 5대 지역만 표시
        region_yearly = region_yearly[region_yearly["region"] != "Other"]

        for r, info in region_map.items():
            r_data = region_yearly[region_yearly["region"] == r]
            plt.plot(
                r_data["year"],
                r_data["pass"],
                color=info["main"],
                linewidth=4,
                marker="s",
                markersize=10,
                label=info["name"],
                zorder=10,
            )

        plt.title("36. 5대 주요 지역별 전체 여객 합계 추이 비교")
        plt.xlabel("연도")
        plt.ylabel("연간 총 여객 수 (명)")
        plt.yscale("linear")  # 규모 차이가 크면 log 고려 가능하나 우선 선형으로
        plt.grid(True, linestyle="-", alpha=0.4)
        plt.legend(title="지역 그룹", fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{SAVE_DIR}/36_route_region_compare.png")
        plt.close()
        print(">>> 36번 지역 통합 비교 시각화 완료")

    print(f">>> 모든 심층 분석 시각화 완료! ( {SAVE_DIR}/ 폴더 확인 )")


if __name__ == "__main__":
    all_data = load_all_data()
    run_25_eda(all_data)
