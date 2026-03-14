import requests
import pandas as pd
import time
import os


def fetch_kosis_data(url):
    """
    KOSIS API 호출 함수
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")
        return None


def collect_kosis_split(metric, base_url, api_key):
    """
    데이터가 너무 많아 40,000셀 제한에 걸리는 경우 연도별로 나누어 수집
    """
    all_data = []
    start_year = int(metric["start"][:4])
    end_year = int(metric["end"][:4])

    print(f"  기간 분할 수집 시작: {start_year}-{end_year}")

    for year in range(start_year, end_year + 1):
        # 해당 연도의 시작/종료 문자열 생성
        s_date = f"{year}01"
        e_date = f"{year}12"

        # metric의 원래 범위와 겹치는 부분만 수집
        s_date = max(s_date, metric["start"])
        e_date = min(e_date, metric["end"])

        if s_date > e_date:
            continue

        print(f"    {year}년 수집 중...", end=" ", flush=True)

        itmId = (
            "T001+T002+T003+"
            if "지연" not in metric["name"] and "결항" not in metric["name"]
            else "T001+"
        )
        objL2 = metric.get("objL2", "ALL")
        objL3 = metric.get("objL3", "")

        url = base_url.format(
            apiKey=api_key,
            itmId=itmId,
            objL2=objL2,
            objL3=objL3,
            start=s_date,
            end=e_date,
            tblId=metric["tblId"],
        )

        data = fetch_kosis_data(url)
        if data and isinstance(data, list):
            all_data.extend(data)
            print("성공")
        else:
            print(f"실패 ({data})")

        time.sleep(0.3)

    return all_data


def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    api_key = "NGM4OTEyZDNmMTYxOTA5ZTM4MTQ4ZWU0YzQ4ZTc1YzU="

    # 수집 대상 지표와 URL
    metrics = [
        {
            "name": "공항별",
            "tblId": "DT_920005_B001",
            "start": "200501",
            "end": "202512",
            "split": True,
        },
        {
            "name": "요일별",
            "tblId": "DT_920005_B002",
            "start": "200501",
            "end": "202512",
        },
        {
            "name": "시간별",
            "tblId": "DT_920005_B003",
            "start": "200501",
            "end": "202512",
            "split": True,
        },
        {
            "name": "국내선_노선별",
            "tblId": "DT_920005_B004",
            "start": "200501",
            "end": "202512",
            "objL2": "B01+",
            "objL3": "C01+",
            "split": True,
        },
        {
            "name": "국제선_지역별",
            "tblId": "DT_920005_B005",
            "start": "200501",
            "end": "202512",
        },
        {
            "name": "지연별_1",
            "tblId": "DT_920005_B006",
            "start": "200501",
            "end": "202212",
        },
        {
            "name": "지연별_2",
            "tblId": "DT_920005_B009",
            "start": "202301",
            "end": "202512",
        },
        {
            "name": "결항별_1",
            "tblId": "DT_920005_B007",
            "start": "200501",
            "end": "202212",
        },
        {
            "name": "결항별_2",
            "tblId": "DT_920005_B010",
            "start": "202301",
            "end": "202512",
        },
        {
            "name": "항공사별",
            "tblId": "DT_920005_B008",
            "start": "200501",
            "end": "202512",
        },
    ]

    base_url = "https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey={apiKey}&itmId={itmId}&objL1=ALL&objL2={objL2}&objL3={objL3}&objL4=&objL5=&objL6=&objL7=&objL8=&format=json&jsonVD=Y&prdSe=M&startPrdDe={start}&endPrdDe={end}&orgId=381&tblId={tblId}"

    for metric in metrics:
        print(f"\n>>> {metric['name']} 데이터 수집 중...")

        if metric.get("split"):
            data = collect_kosis_split(metric, base_url, api_key)
        else:
            itmId = (
                "T001+T002+T003+"
                if "지연" not in metric["name"] and "결항" not in metric["name"]
                else "T001+"
            )
            objL2 = metric.get("objL2", "ALL")
            objL3 = metric.get("objL3", "")

            url = base_url.format(
                apiKey=api_key,
                itmId=itmId,
                objL2=objL2,
                objL3=objL3,
                start=metric["start"],
                end=metric["end"],
                tblId=metric["tblId"],
            )
            data = fetch_kosis_data(url)

        if data:
            if isinstance(data, list):
                df = pd.DataFrame(data)
                filename = f"data/kosis_{metric['name']}_2005_2025.csv"
                df.to_csv(filename, index=False, encoding="utf-8-sig")
                print(f"  최종 성공: {filename} ({len(df)}행)")
            else:
                print(f"  실패: 예기치 않은 데이터 형식 ({data})")
        else:
            print(f"  실패: 데이터를 가져오지 못했습니다.")

        time.sleep(0.5)


if __name__ == "__main__":
    main()
