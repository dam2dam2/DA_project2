import json
import os

def analyze_structure():
    file_path = "/Users/dami/innercircle/DA_project2/data/investigate_next_data.json"
    if not os.path.exists(file_path):
        print("Json file not found!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Next.js의 react-query 상태를 확인
    try:
        queries = data['props']['pageProps']['dehydratedState']['queries']
        print(f"Total react-query queries: {len(queries)}")
        
        for q in queries:
            key = q.get('queryKey', [])
            state = q.get('state', {})
            data_obj = state.get('data', {})
            
            # 리뷰 관련 키 탐색
            if isinstance(key, list) and 'review' in str(key).lower():
                print(f"\n[💡Found Review Query Key]: {key}")
                
                if isinstance(data_obj, dict):
                    print("Data Keys:", list(data_obj.keys()))
                    # 리뷰 갯수와 페이지네이션 정보 확인
                    if 'totalCount' in data_obj:
                        print(f"Total Reviews Count from direct key: {data_obj['totalCount']}")
                    if 'page' in data_obj:
                        print(f"Pagination Info: {data_obj['page']}")
                    
                    if 'reviews' in data_obj:
                        reviews = data_obj['reviews']
                        print(f"Current chunk review count: {len(reviews)}")
                        if reviews and isinstance(reviews, list):
                            print(f"Sample Review 1 keys: {list(reviews[0].keys())}")
                            print(f"Sample Content: {reviews[0].get('content', 'No content')[:50]}...")
            
            # 상품 정보 쿼리 탐색 (상품 ID 등을 확인하기 위함)
            elif isinstance(key, list) and 'product' in str(key).lower():
                print(f"\n[🛒Found Product Query Key]: {key}")

    except KeyError as e:
        print("KeyError! Structure might be different:", e)

if __name__ == "__main__":
    analyze_structure()
