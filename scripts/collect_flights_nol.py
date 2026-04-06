import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import os

# 야놀자 항공권 검색 API 기본 정보
BASE_URL = "https://tour.yanolja.com/air/air-api/nol-air-web-api"

# 분석 대상 3개 지역 (휴양형 2, 관광형 1)
DESTINATIONS = {
    "다낭": "DAD",
    "나트랑": "CXR",
    "싱가포르": "SIN"
}

def get_search_id(dest_code, departure_date, return_date=None):
    if return_date:
        route = f"CITY:SEL-CITY:{dest_code}/{departure_date}/CITY:{dest_code}-CITY:SEL/{return_date}"
        referer = f"https://tour.yanolja.com/air/search/c:SEL-c:{dest_code}-{departure_date.replace('-', '')}/c:{dest_code}-c:SEL-{return_date.replace('-', '')}?cabin=ECONOMY&infant=0&child=0&adult=1"
    else:
        route = f"CITY:SEL-CITY:{dest_code}/{departure_date}"
        referer = f"https://tour.yanolja.com/air/search/c:SEL-c:{dest_code}-{departure_date.replace('-', '')}?cabin=ECONOMY&infant=0&child=0&adult=1"

    url = f"{BASE_URL}/flights/search/{route}?adult=1&child=0&infant=0&cabins=ECONOMY&freeBaggageOnly=false"
    
    headers = {
        "Accept": "*/*",
        "Referer": referer,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("key")
    except Exception as e:
        print(f"Error getting search ID for {dest_code} {departure_date}: {e}")
        return None

def wait_for_completion(search_id):
    if not search_id:
        return False
        
    url = f"{BASE_URL}/international/flights/search/v2/{search_id}/status"
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    
    for _ in range(15):  # 최대 30초 대기
        try:
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == "COMPLETE" or data.get("progress", 0) >= 100:
                    return True
            time.sleep(2)
        except:
            time.sleep(2)
    return True

def fetch_flight_results(search_id, dest_name):
    if not search_id:
        return []

    wait_for_completion(search_id)

    url = f"{BASE_URL}/international/flights/search/v2/{search_id}"
    payload = {"pageNumber": 1, "pageSize": 100, "filter": {}}
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    
    for attempt in range(3):
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            flights = []
            contents = data.get("contents", [])
            
            for item in contents:
                price = item.get("adultPrice", 0)
                schedules = item.get("schedules", [])
                
                flight_info = {
                    "destination": dest_name,
                    "search_id": search_id,
                    "total_price": price,
                }
                
                for i, schedule in enumerate(schedules):
                    prefix = "departure" if i == 0 else "return"
                    carrier = schedule.get("marketingCarriers", [{}])[0].get("name", "N/A")
                    flight_time = schedule.get("totalFlightTime", "N/A")
                    stop = schedule.get("stop", 0)
                    add_day = schedule.get("addDay", 0)
                    
                    baggage = schedule.get("freeBaggage", {})
                    b_allowance = baggage.get("allowance")
                    b_unit = baggage.get("unit", "")
                    baggage_str = f"{b_allowance} {b_unit}" if b_allowance is not None else "정보 없음"
                    
                    segments = schedule.get("segments", [])
                    if segments:
                        dep_time = segments[0].get("departure", {}).get("at", "N/A")
                        arr_time = segments[-1].get("arrival", {}).get("at", "N/A")
                    else:
                        dep_time, arr_time = "N/A", "N/A"
                    
                    flight_info.update({
                        f"{prefix}_carrier": carrier,
                        f"{prefix}_flight_time": flight_time,
                        f"{prefix}_stop": stop,
                        f"{prefix}_add_day": add_day,
                        f"{prefix}_baggage": baggage_str,
                        f"{prefix}_dep_at": dep_time,
                        f"{prefix}_arr_at": arr_time,
                    })
                
                flights.append(flight_info)
            return flights
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {search_id}: {e}")
            time.sleep(3)
            
    return []

def main():
    start_date = datetime(2026, 3, 22)
    days_to_collect = 1 # 테스트를 위해 1일치. 늘릴 수 있습니다.
    
    all_data = []
    print("=== 다낭/나트랑/싱가포르 항공권 데이터 수집 시작 (수하물 정보 포함) ===")
    
    for dest_name, dest_code in DESTINATIONS.items():
        print(f"\n[{dest_name}] 비행편 수집 중...")
        for i in range(days_to_collect):
            current_date = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            
            # 1. 편도 수집
            print(f"  > [{current_date}] 편도 검색...")
            sid_ow = get_search_id(dest_code, current_date)
            ow_results = fetch_flight_results(sid_ow, dest_name)
            for res in ow_results:
                res["type"] = "One-way"
                all_data.append(res)
            
            # 2. 왕복 수집 (예시: 3일 뒤 귀국)
            return_date = (start_date + timedelta(days=i+3)).strftime("%Y-%m-%d")
            print(f"  > [{current_date} ~ {return_date}] 왕복 검색...")
            sid_rt = get_search_id(dest_code, current_date, return_date)
            rt_results = fetch_flight_results(sid_rt, dest_name)
            for res in rt_results:
                res["type"] = "Round-trip"
                all_data.append(res)
                
            time.sleep(1)
    
    if all_data:
        df = pd.DataFrame(all_data)
        os.makedirs("data", exist_ok=True)
        cols = [
            "destination", "type", "total_price", 
            "departure_carrier", "departure_flight_time", "departure_stop", "departure_add_day", "departure_baggage", "departure_dep_at", "departure_arr_at",
            "return_carrier", "return_flight_time", "return_stop", "return_add_day", "return_baggage", "return_dep_at", "return_arr_at"
        ]
        actual_cols = [c for c in cols if c in df.columns]
        df = df[actual_cols]
        
        output_path = "data/flights_nol_multi.csv"
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n총 {len(df)}건의 항공 데이터를 수집하여 '{output_path}'에 저장했습니다.")
    else:
        print("\n수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
