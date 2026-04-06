import requests
from bs4 import BeautifulSoup
import json
import os

url = "https://tour.yanolja.com/package/products/ASVNS09700"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def analyze_page():
    print(f"URL 요청 중: {url}")
    response = requests.get(url, headers=headers)
    html = response.text
    
    print(f"응답 상태 코드: {response.status_code}")
    print(f"HTML 전체 길이: {len(html)} characters")
    
    # data 폴더가 없으면 생성
    os.makedirs("/Users/dami/innercircle/DA_project2/data", exist_ok=True)
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Next.js 데이터 구조 탐색
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        print("\n[✅ __NEXT_DATA__ 스크립트를 찾았습니다. 이곳에 보통 리뷰 등 전체 데이터가 들어있습니다.]")
        data = json.loads(next_data.string)
        
        # 분석을 위해 임시 json 파일로 저장
        with open("/Users/dami/innercircle/DA_project2/data/investigate_next_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("-> Next.js 데이터를 저장했습니다: data/investigate_next_data.json")
    else:
        print("\n[❌ __NEXT_DATA__ 구조를 찾지 못했습니다.]")
        
    # 2. 다른 공통 데이터 구조 탐색
    if "window.__INITIAL_STATE__" in html:
        print("[✅ window.__INITIAL_STATE__ 구조를 찾았습니다.]")
    
    # 3. 혹시 모르니 원본 HTML 저장
    with open("/Users/dami/innercircle/DA_project2/data/investigate_raw.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("-> 원본 HTML을 저장했습니다: data/investigate_raw.html")

if __name__ == "__main__":
    analyze_page()
