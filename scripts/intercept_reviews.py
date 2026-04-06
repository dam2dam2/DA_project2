from playwright.sync_api import sync_playwright
import json

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    found_api = False

    def handle_response(response):
        nonlocal found_api
        if response.request.resource_type in ["fetch", "xhr"]:
            try:
                # 응답 데이터를 텍스트로 받아옴
                text = response.text()
                # 실제 리뷰어 이름이나 '리뷰' 텍스트가 포함되어 있는지 확인
                if "권*련" in text or "김*미" in text or "최*미" in text:
                    print(f"\n[🚀 발견 완료!] 실제 리뷰 데이터가 포함된 API 호출 주소: {response.url}")
                    with open("/Users/dami/innercircle/DA_project2/data/investigate_api_response.json", "w", encoding="utf-8") as f:
                        f.write(text)
                    print("  => API 응답 전체 데이터를 investigate_api_response.json 에 저장했습니다.")
                    found_api = True
            except Exception as e:
                pass

    page.on("response", handle_response)
    
    print("야놀자 상품 상세 페이지 접속 (domcontentloaded)...")
    try:
        page.goto("https://tour.yanolja.com/package/products/ASVNS09700", wait_until="domcontentloaded", timeout=20000)
    except Exception as e:
        pass
        
    print("스크롤 다운 및 버튼 탐색 중...")
    for i in range(15):
        if found_api:
            print("=> 타겟 API를 성공적으로 저장했습니다. 브라우저를 닫습니다.")
            break
        try:
            page.evaluate("window.scrollBy(0, 1000)")
            # 화면 내 '리뷰' 버튼이 있다면 클릭 유도
            page.evaluate('''
                document.querySelectorAll("button, div, li").forEach(el => {
                    if(el.innerText && el.innerText.includes("리뷰") && el.innerText.length < 10) el.click();
                });
            ''')
        except:
            pass
        page.wait_for_timeout(1000)
        
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
