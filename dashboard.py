import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob

# 페이지 설정
st.set_page_config(page_title="항공 통계 익스트림 대시보드", layout="wide")

st.title("🚀 항공 통계 종합 인사이트 대시보드")


# 데이터 로드 함수
@st.cache_data
def get_base_data():
    try:
        # UTF-8 BOM 대응을 위해 utf-8-sig 사용
        df = pd.read_csv("data/airport_flights_2002_2025.csv", encoding="utf-8-sig")
        p = pd.read_csv("data/airport_passengers_2002_2025.csv", encoding="utf-8-sig")

        # 숫자형 변환 전 콤마 제거 및 공백 정리
        for col in ["flight", "arrFlight", "depFlight"]:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "")
                    .replace("-", "0")
                    .astype(float)
                )

        for col in ["passenger", "arrPassenger", "depPassenger"]:
            if col in p.columns:
                p[col] = (
                    p[col]
                    .astype(str)
                    .str.replace(",", "")
                    .replace("-", "0")
                    .astype(float)
                )

        df = pd.merge(df, p, on=["year", "time"])
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()


# 사이드바 설정
st.sidebar.header("📊 분석 통합 필터")
year_range = st.sidebar.slider("분석 연도 범위", 2002, 2025, (2002, 2025))

# 메인 지표 계산
base_df = get_base_data()
if not base_df.empty:
    filtered_base = base_df[
        (base_df["year"] >= year_range[0]) & (base_df["year"] <= year_range[1])
    ]
    yearly_sum = (
        filtered_base.groupby("year")[["flight", "passenger"]].sum().reset_index()
    )

    # KPI 카드
    cols = st.columns(4)
    cols[0].metric("누적 여객 수", f"{yearly_sum['passenger'].sum():,.0f} 명")
    cols[1].metric("누적 운항 편수", f"{yearly_sum['flight'].sum():,.0f} 편")
    cols[2].metric("연평균 여객", f"{yearly_sum['passenger'].mean():,.0f} 명")
    cols[3].metric("최대 여객 (연간)", f"{yearly_sum['passenger'].max():,.0f} 명")
else:
    st.warning("데이터를 불러올 수 없습니다.")

st.markdown("---")

# 대분류 탭 구성
tabs = st.tabs(
    [
        "📈 장기 트렌드",
        "🕓 수요 패턴",
        "👥 여객/운송 특성",
        "🌐 노선 및 시장",
        "⚠️ 정시성 장애",
        "🌦️ 기상 상관분석",
    ]
)

# 이미지 경로 헬퍼
IMG_DIR = "images"

with tabs[0]:
    st.header("1. 항공 시장 장기 트렌드 분석 (2002-2025)")
    st.info("20여 년간의 항공 운송량 변화를 통해 시장의 성장성과 탄력성을 분석합니다.")
    c1, c2 = st.columns(2)
    with c1:
        st.image(
            f"{IMG_DIR}/01_yearly_pax.png",
            caption="연도별 여객 추이",
            use_container_width=True,
        )
    with c2:
        st.image(
            f"{IMG_DIR}/02_yearly_flight.png",
            caption="연도별 운항 추이",
            use_container_width=True,
        )
    st.image(
        f"{IMG_DIR}/03_yearly_cargo.png",
        caption="연도별 화물 수송량 추이 (안정적 성장세)",
        use_container_width=True,
    )

with tabs[1]:
    st.header("2. 시즌 및 시간대별 세부 수요 패턴")
    st.markdown("#### 📅 계절 및 요일별 분포")
    c1, c2 = st.columns(2)
    with c1:
        st.image(
            f"{IMG_DIR}/04_monthly_season.png",
            caption="월별 계절성 (성수기 분석)",
            use_container_width=True,
        )
    with c2:
        st.image(
            f"{IMG_DIR}/05_day_dist.png",
            caption="요일별 운송량 분포",
            use_container_width=True,
        )

    st.markdown("#### ⏰ 시간대별 혼잡도 분석")
    c3, c4 = st.columns(2)
    with c3:
        st.image(
            f"{IMG_DIR}/06_hourly_pax.png",
            caption="시간대별 평균 여객 피크",
            use_container_width=True,
        )
    with c4:
        st.image(
            f"{IMG_DIR}/07_hourly_flight.png",
            caption="시간대별 운항 슬롯 점유",
            use_container_width=True,
        )

with tabs[2]:
    st.header("3. 여객 및 운송 세부 특성 심층 분석")
    st.info("운항 성격과 여객 유형에 따른 세부 비중을 시각화합니다.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image(
            f"{IMG_DIR}/08_sched_pie.png",
            caption="정기 vs 부정기",
            use_container_width=True,
        )
    with col2:
        st.image(
            f"{IMG_DIR}/09_pax_type_pie.png",
            caption="유임 vs 환승",
            use_container_width=True,
        )
    with col3:
        st.image(
            f"{IMG_DIR}/10_direction_pie.png",
            caption="출발 vs 도착",
            use_container_width=True,
        )

    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        st.image(
            f"{IMG_DIR}/11_dom_intl_ratio.png",
            caption="국내선 vs 국제선 비중",
            use_container_width=True,
        )
    with c_sub2:
        st.image(
            f"{IMG_DIR}/12_airport_share.png",
            caption="주요 거점 공항별 분담률",
            use_container_width=True,
        )

with tabs[3]:
    st.header("4. 노선 점유율 및 항공사별 성과")
    st.markdown("#### 🌐 국제선 노선 지표")
    st.image(
        f"{IMG_DIR}/13_intl_region.png",
        caption="국제선 지역별 수요 분포 (아시아 허브)",
        use_container_width=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.image(
            f"{IMG_DIR}/14_top15_intl.png",
            caption="상위 15개 국제 노선",
            use_container_width=True,
        )
    with c2:
        st.image(
            f"{IMG_DIR}/15_intl_growth.png",
            caption="국제선 연간 성장률 추이",
            use_container_width=True,
        )

    st.markdown("#### 🇰🇷 국내선 및 항공사 현황")
    c3, c4 = st.columns(2)
    with c3:
        st.image(
            f"{IMG_DIR}/16_top10_dom.png",
            caption="국내 상위 노선 (제주 중심)",
            use_container_width=True,
        )
    with c4:
        st.image(
            f"{IMG_DIR}/17_airline_share.png",
            caption="항공사별 시장 점유율",
            use_container_width=True,
        )

with tabs[4]:
    st.header("5. 항공 정시성 장애 (지연 및 결항) 리포트")
    st.image(
        f"{IMG_DIR}/18_delay_trend.png",
        caption="연도별 지연 발생 빈도",
        use_container_width=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.image(
            f"{IMG_DIR}/19_monthly_delay.png",
            caption="월별 지연 집중도",
            use_container_width=True,
        )
    with c2:
        st.image(
            f"{IMG_DIR}/20_cancel_trend.png",
            caption="연도별 결항 발생 건수",
            use_container_width=True,
        )
    st.image(
        f"{IMG_DIR}/21_delay_cancel_corr.png",
        caption="공항별 지연-결항 상관관계",
        use_container_width=True,
    )

with tabs[5]:
    st.header("6. 기상 요인 복합 상관관계 및 영향도")
    st.success(
        "💡 통계 결과: 풍속(Wind Speed)이 항공기 결항을 유발하는 가장 직접적인 기상 인자로 나타났습니다."
    )
    st.image(
        f"{IMG_DIR}/22_weather_heatmap.png",
        caption="기상 요인-결항 상관분석 히트맵",
        use_container_width=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.image(
            f"{IMG_DIR}/23_wind_reg.png",
            caption="풍속과 결항의 선형 회귀 분석",
            use_container_width=True,
        )
    with c2:
        st.image(
            f"{IMG_DIR}/24_precip_bubble.png",
            caption="강수량-풍속-기온 복합 분석",
            use_container_width=True,
        )
    st.image(
        f"{IMG_DIR}/25_seasonal_variation.png",
        caption="계절별 결항 발생 편차 및 아웃라이어 분석",
        use_container_width=True,
    )

st.sidebar.markdown("---")
st.sidebar.info("🎯 25개 이상의 전문 분석 모듈이 실시간으로 구동되고 있습니다.")
st.sidebar.caption("Data Source: Incheon Airport, Airportal, KOSIS, KMA")
