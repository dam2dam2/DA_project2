import requests
import pandas as pd
import time
import os

# 상품 구조(리조트 등급, 가격대 등)를 비교할 핵심 3개 지역 및 공항코드
DESTINATIONS = {"다낭": "DAD", "나트랑": "CXR", "싱가포르": "SIN"}
MAX_PAGES = 10 # 각 지역당 최대 수집 페이지 (너무 많아지는 것을 방지)

def fetch_accommodations(dest_name, dest_code):
    all_accommodations = []
    page = 1
    
    url = "https://nol.yanolja.com/discovery/api/list/universal-search/v1-global/list"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    }
    
    while page <= MAX_PAGES:
        # 공유해주신 쿼리 구조를 그대로 활용합니다. 날짜는 임의의 미래 일정으로 설정
        payload = {
            "keyword": dest_name,
            "filters": [{"key": "AVAILABLE_ONLY", "code": "AVAILABLE_ONLY"}],
            "sort": "RECOMMEND",
            "category": "GLOBAL_ACCOMMODATION",
            "userLocation": {"latitude": 37.56657, "longitude": 126.97817, "locationType": "DEFAULT", "locationTime": 1773973869},
            "localAccommodation": {"checkInDate": "2026-04-11", "checkOutDate": "2026-04-13", "capacityAdults": 2, "childrenAges": []},
            "globalAccommodation": {
                "checkInDate": "2026-04-11",
                "checkOutDate": "2026-04-13",
                "rooms": [{"capacityAdults": 2, "childrenAges": []}]
            },
            "extraInfo": {
                "flightInfo": {"arrivalPlaceTypeCode": "AIRPORT", "arrivalPlaceCode": dest_code, "outboundDepartureDate": "2026-04-11", "inboundDepartureDate": "2026-04-13"},
                "availableTabKeys": ["GLOBAL_ACCOMMODATION", "GLOBAL_TNA", "FLIGHT", "ENTERTAINMENT", "GLOBAL_PACKAGE"]
            },
            "page": page
        }
        
        print(f"[{dest_name}] 숙소 {page}페이지 수집 중...")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            items = data.get("items", [])
            # 숙소 상품 데이터만 필터링 (광고나 기타 배너 제외)
            product_items = [item for item in items if item.get("type") == "PRODUCT_ITEM"]
            
            if not product_items:
                break # 더 이상 데이터가 없으면 수집 종료
                
            for item in product_items:
                item_data = item.get("data", {})
                review = item_data.get("review", {})
                prices = item_data.get("prices", [])
                
                # 할인 가격 추출 (숫자 형태로 변환)
                discount_price_str = prices[0].get("discountPrice", "0") if prices else "0"
                # "189,292" 형태에서 쉼표 제거
                discount_price_num = int(discount_price_str.replace(",", "")) if isinstance(discount_price_str, str) and discount_price_str else 0
                
                acc_info = {
                    "destination": dest_name,
                    "title": item_data.get("title", ""),
                    "category": item_data.get("category", ""), # 예: "리조트 ・ 5성급"
                    "location": item_data.get("locationDetails", [""])[0] if item_data.get("locationDetails") else "",
                    "review_score": review.get("score", "0"),
                    "review_count": review.get("count", "0"),
                    "discount_price": discount_price_num
                }
                all_accommodations.append(acc_info)
                
            page += 1
            time.sleep(1) # 차단 방지를 위해 1초 휴식
            
        except Exception as e:
            print(f"[{dest_name}] 수집 중 오류: {e}")
            break
            
    return all_accommodations

def main():
    all_data = []
    
    print("=== 해외 숙소(다낭/나트랑/싱가포르) 데이터 수집 시작 ===")
    for dest, code in DESTINATIONS.items():
        accs = fetch_accommodations(dest, code)
        all_data.extend(accs)
        
    if all_data:
        df = pd.DataFrame(all_data)
        os.makedirs("data", exist_ok=True)
        output_file = "data/accommodations_nol.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig", mode='w')
        print(f"\n성공! 총 {len(df)}건의 숙소 상품을 '{output_file}'에 저장했습니다.")
    else:
        print("\n수집된 데이터가 없습니다.")

if __name__ == "__main__":
    main()
