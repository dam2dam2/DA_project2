import requests
import pandas as pd
import time
import os

# docs/nol.md에서 확인된 패키지 검색 Query ID
# 사용자가 브라우저(Network 창)에서 찾은 고유 ID입니다.
DESTINATION_QUERIES = {
    "목적지_A(다낭_추정)": "a9dbaa65-0bab-4b9f-a24c-166dfc8fe13f",
    "목적지_B(나트랑_추정)": "fc6fc255-4394-48f6-9b0a-a2c61068181e"
    # "싱가포르": "" # 싱가포르 검색 시 Network 탭에서 나오는 queryId를 여기에 추가해주시면 됩니다.
}

def fetch_packages(dest_name, query_id):
    all_packages = []
    page = 1
    max_page = 1
    
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "referer": "https://tour.yanolja.com/",
    }
    
    # max_page까지만 반복해서 수집합니다.
    while page <= max_page:
        url = f"https://tour.yanolja.com/tour-api/package-hub/search?queryId={query_id}&page={page}&pageSize=10"
        print(f"[{dest_name}] {page}페이지 수집 중... (예상 최대: {max_page}페이지)")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status() # 오류 발생 시 즉시 탈출
            data = response.json()
            
            # 1페이지 데이터에서 전체 페이지 수(maxPage) 확인
            if page == 1:
                max_page = data.get("page", {}).get("maxPage", 1)
                
            documents = data.get("documents", [])
            if not documents: # 더 이상 수집할 데이터가 없으면 탈출
                break 
                
            for doc in documents:
                # 테마(관광, 휴양 등) 및 이용 항공사(LCC, FSC 분리 가능) 목록 조인
                themes = [t.get("name") for t in doc.get("themes", [])]
                airlines = [a.get("name") for a in doc.get("airlines", [])]
                review = doc.get("review", {})
                duration = doc.get("duration", {}).get("nightsAndDays", "")
                
                # 분석 목적에 맞추어 상품 구조(일정, 가격, 카테고리 등) 추출
                pkg_info = {
                    "destination": dest_name,
                    "product_id": doc.get("id"),
                    "name": doc.get("name"),
                    "description": doc.get("description"),
                    "category": doc.get("category", {}).get("name", ""),
                    "themes": ", ".join(themes),
                    "departure_date": doc.get("date"),
                    "original_price": doc.get("price", 0),
                    "discount_price": doc.get("discountPrice", {}).get("amount", doc.get("price", 0)),
                    "airlines": ", ".join(airlines),
                    "duration": duration,
                    "review_count": review.get("count", 0),
                    "review_score": review.get("score", 0.0),
                    "shopping_count": doc.get("shoppingCount", 0), # 쇼핑 횟수(패키지 중요 요소)
                    "product_grade": doc.get("productGrade", "")
                }
                all_packages.append(pkg_info)
                
            page += 1
            time.sleep(1) # 차단을 피하기 위해 1초 대기 (매우 중요)
            
        except requests.exceptions.HTTPError as e:
            print(f"[{dest_name}] HTTP 통신 에러가 발생했습니다. (queryId가 만료되었을 수 있습니다): {e}")
            break
        except Exception as e:
            print(f"[{dest_name}] {page}페이지 수집 중 에러 발생: {e}")
            break
            
    return all_packages

def main():
    all_data = []
    
    print("=== 야놀자 패키지 상품 데이터 자동 수집 시작 ===")
    for dest_name, q_id in DESTINATION_QUERIES.items():
        if not q_id:
            continue
        packages = fetch_packages(dest_name, q_id)
        all_data.extend(packages)
        
    if all_data:
        df = pd.DataFrame(all_data)
        os.makedirs("data", exist_ok=True)
        output_file = "data/packages_nol.csv"
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n성공! 총 {len(df)}건의 패키지 상품을 '{output_file}'에 저장 완료했습니다.")
    else:
        print("\n수집된 데이터가 없습니다. 브라우저에서 새로운 queryId를 복사하여 코드에 붙여넣어 주세요.")

if __name__ == "__main__":
    main()
