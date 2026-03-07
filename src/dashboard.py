import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os

# --- 페이지 설정 ---
st.set_page_config(
    page_title="서울시 공공자전거 대여 데이터 대시보드 (2015-2025)",
    page_icon="🚲",
    layout="wide",
)


# --- 1. 데이터 로드 ---
@st.cache_data
def load_data():
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "data",
        "bike_weather_combined.csv",
    )
    if not os.path.exists(file_path):
        # 병합 파일이 없으면 기존 대여 데이터라도 로드 시도
        file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "data",
            "daily_bike_rentals_2015_2025.csv",
        )
        if not os.path.exists(file_path):
            return None

    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["date"].dt.day_name()
    return df


df = load_data()

if df is None:
    st.error("데이터 파일을 찾을 수 없습니다. 전처리가 필요합니다.")
    st.stop()

# --- 사이드바 필터 ---
st.sidebar.header("🔍 필터 설정")
year_list = sorted(df["year"].unique())
selected_years = st.sidebar.multiselect("연도 선택", year_list, default=year_list)

filtered_df = df[df["year"].isin(selected_years)]

# --- 메인 대시보드 ---
st.title("🚲 서울시 공공자전거(따릉이) 이용 및 기상 분석 대시보드")
st.markdown(
    "2015년부터 2025년까지의 대여 데이터와 기상청(ASOS) 데이터를 결합한 통합 분석 대시보드입니다."
)

# KPI 지표
k1, k2, k3, k4 = st.columns(4)
total_rentals = filtered_df["count"].sum()
avg_daily_rentals = filtered_df["count"].mean()
avg_temp = filtered_df["temp"].mean() if "temp" in filtered_df.columns else 0
total_precip = filtered_df["precip"].sum() if "precip" in filtered_df.columns else 0

k1.metric("총 대여 건수", f"{total_rentals:,}건")
k2.metric("일평균 대여 건수", f"{avg_daily_rentals:,.0f}건")
k3.metric("평균 기온", f"{avg_temp:.1f}°C")
k4.metric("총 강수량", f"{total_precip:,.1f}mm")

st.divider()

# Tab 구성
tabs = st.tabs(
    ["📊 트렌드 분석", "📅 시기별 분석", "🌡️ 날씨 상관분석", "📋 데이터 상세"]
)

# Tab 1: 트렌드 분석
with tabs[0]:
    st.subheader("📈 연도별/월별 대여 트렌드")

    # 연도별 합계 시각화
    yearly_agg = filtered_df.groupby("year")["count"].sum().reset_index()
    fig_yearly = px.bar(
        yearly_agg,
        x="year",
        y="count",
        title="연도별 총 대여 건수",
        labels={"year": "연도", "count": "대여 건수"},
        color="count",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_yearly, use_container_width=True)

    # 일별 추이 시각화
    st.subheader("일별 대여 건수 추이")
    fig_daily = px.line(
        filtered_df,
        x="date",
        y="count",
        title="일별 대여 건수 시점 변화",
        labels={"date": "날짜", "count": "대여 건수"},
    )
    st.plotly_chart(fig_daily, use_container_width=True)

# Tab 2: 시기별 분석
with tabs[1]:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 월별 평균 대여 건수")
        month_agg = filtered_df.groupby("month")["count"].mean().reset_index()
        fig_month = px.line(
            month_agg,
            x="month",
            y="count",
            markers=True,
            title="월별 평균 이용량 (계절성 확인)",
            labels={"month": "월", "count": "평균 대여 건수"},
        )
        fig_month.update_xaxes(tickmode="linear", tick0=1, dtick=1)
        st.plotly_chart(fig_month, use_container_width=True)

    with col2:
        st.subheader("요일별 데이터 분포")
        # 요일 순서 정렬
        day_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        fig_dow = px.box(
            filtered_df,
            x="day_of_week",
            y="count",
            category_orders={"day_of_week": day_order},
            title="요일별 대여 건수 분포",
            labels={"day_of_week": "요일", "count": "대여 건수"},
        )
        st.plotly_chart(fig_dow, use_container_width=True)

# Tab 3: 날씨 상관분석
with tabs[2]:
    if "temp" in filtered_df.columns:
        st.subheader("☀️ 기상 요인에 따른 이용량 변화")

        c1, c2 = st.columns(2)

        with c1:
            # 기온 vs 대여건수 산점도
            st.markdown("##### 기온과 대여량의 관계")
            fig_temp = px.scatter(
                filtered_df,
                x="temp",
                y="count",
                trendline="ols",
                title="기온 vs 대여 건수",
                labels={"temp": "평균 기온 (°C)", "count": "대여 건수"},
                opacity=0.5,
            )
            st.plotly_chart(fig_temp, use_container_width=True)

        with c2:
            # 강수량 유무에 따른 이용량 비교
            st.markdown("##### 강수 유무에 따른 이용량 차이")
            filtered_df["is_rainy"] = filtered_df["precip"].apply(
                lambda x: "비/눈 옴" if x > 0 else "안 옴"
            )
            rain_agg = filtered_df.groupby("is_rainy")["count"].mean().reset_index()
            fig_rain = px.bar(
                rain_agg,
                x="is_rainy",
                y="count",
                title="강수 유무별 평균 대여 건수",
                labels={"is_rainy": "강수 유무", "count": "평균 대여 건수"},
                color="is_rainy",
            )
            st.plotly_chart(fig_rain, use_container_width=True)

        st.divider()
        st.subheader("🧩 기상-이용 상관계수 히트맵")
        corr = filtered_df[["count", "temp", "precip", "wind_speed", "humidity"]].corr()
        fig_heat = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto",
            title="요인별 상관계수",
            color_continuous_scale="RdBu_r",
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.warning("기상 데이터가 통합되지 않았습니다.")

# Tab 4: 데이터 상세
with tabs[3]:
    st.subheader("📄 데이터 레코드")
    st.dataframe(
        filtered_df.sort_values("date", ascending=False), use_container_width=True
    )
