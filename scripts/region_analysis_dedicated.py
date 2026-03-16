import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
import numpy as np


def run_region_analysis():
    df_det = pd.read_csv("data/airportal_route_intl_detailed_2018_2025.csv")
    SAVE_DIR = "images"
    os.makedirs(SAVE_DIR, exist_ok=True)

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

    def assign_region(name):
        for r, info in region_map.items():
            if any(kw in str(name) for kw in info["kw"]):
                return r
        return "Other"

    df_det["region"] = df_det["airport_name"].apply(assign_region)
    df_det["ym_int"] = df_det["year_month"].astype(int)
    df_det["year"] = df_det["ym_int"] // 100

    # 정상 운영 월 정의
    monthly_total_pass = df_det.groupby("year_month")["pass"].sum()
    valid_months = monthly_total_pass[monthly_total_pass > 100000].index.tolist()

    df_normal = df_det[df_det["year_month"].isin(valid_months)]
    df_normal = df_normal[
        (df_normal["ym_int"] < 202001) | (df_normal["ym_int"] > 202212)
    ]

    # 31-35. 지역별 개별 노선 추이
    plot_idx = 31
    for r, info in region_map.items():
        df_r = df_det[df_det["region"] == r]
        df_r_normal = df_normal[df_normal["region"] == r]

        min_pass_r = df_r_normal.groupby("airport_name")["pass"].min()
        targets_r = min_pass_r[min_pass_r >= 10000].index.tolist()

        bg_r = df_r[~df_r["airport_name"].isin(targets_r)]["airport_name"].unique()

        plt.figure(figsize=(14, 7))
        all_r_trend = df_r.groupby(["year", "airport_name"])["pass"].sum().reset_index()

        for node in bg_r:
            node_data = all_r_trend[all_r_trend["airport_name"] == node]
            plt.plot(
                node_data["year"],
                node_data["pass"],
                color="#E0E0E0",
                alpha=0.15,
                linewidth=0.5,
            )

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
            f"{plot_idx}. {info['name']} 지역 우량 노선 여객 추이 (정상 월 1만+)",
            fontsize=15,
        )
        plt.xlabel("연도")
        plt.ylabel("연간 여객 수 (명)")
        plt.grid(True, linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.savefig(f"{SAVE_DIR}/{plot_idx}_route_{r.lower()}.png")
        plt.close()
        print(f">>> {plot_idx}번 ({info['name']}) 완료.")
        plot_idx += 1

    # 36. 지역별 합계 통합 비교
    plt.figure(figsize=(15, 8))
    region_yearly = df_det.groupby(["year", "region"])["pass"].sum().reset_index()
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

    plt.title("36. 5대 주요 지역별 전체 여객 합계 추이 비교", fontsize=18)
    plt.xlabel("연도")
    plt.ylabel("연간 총 여객 수 (명)")
    plt.grid(True, linestyle="-", alpha=0.4)
    plt.legend(title="지역 그룹", fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{SAVE_DIR}/36_route_region_compare.png")
    plt.close()
    print(">>> 36번 완료.")


if __name__ == "__main__":
    run_region_analysis()
