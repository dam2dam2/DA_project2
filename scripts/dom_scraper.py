from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time

def scrape_product(playwright, url):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    print(f"상품 페이지 접속 중... {url}")
    page.goto(url, wait_until="domcontentloaded")
    
    print("리뷰 로딩을 위해 하단으로 스크롤 중...")
    for _ in range(5):
        page.evaluate("window.scrollBy(0, 1000)")
        page.wait_for_timeout(1000)
    
    print("'더보기' 버튼 클릭을 시작합니다...")
    clicks = 0
    while clicks < 10:  # 테스트 용도로 최대 10번만 확장
        try:
            # '리뷰 더보기' 역할을 하는 버튼 찾기
            more_btn = page.locator("button", has_text="리뷰 더보기")
            if more_btn.count() == 0:
                more_btn = page.locator("button:has-text('더보기')")
            
            # 더보기 버튼 중에 '리뷰'와 관련된 버튼을 좀 더 구체적으로 필터할 수도 있지만, 우선 텍스트 매칭 위주로 진행
            if more_btn.count() > 0:
                # 첫번째 더보기 버튼 요소를 강제 클릭 (모달이나 헤더 뒤에 가려질 수 있으므로 JS click 사용)
                more_btn.first.evaluate("node => node.click()")
                clicks += 1
                print(f" -> '더보기' 버튼을 클릭했습니다. (누적 {clicks}회)")
                page.wait_for_timeout(1500)
            else:
                print("더 이상 '더보기' 버튼이 없습니다.")
                break
        except Exception as e:
            print("더보기 버튼 클릭 중 오류 발생 (종료):", e)
            break
            
    print("현재 띄워진 전체 HTML 데이터를 추출합니다...")
    html = page.content()
    browser.close()
    
    print("BeautifulSoup을 이용해 리뷰 텍스트 파싱 중...")
    soup = BeautifulSoup(html, 'html.parser')
    reviews = []
    
    # class 이름에 'comment__CommentText' 가 포함된 영역이 리뷰 내용임 (앞서 사용자 제공 HTML 참조)
    comment_tags = soup.find_all("p", class_=lambda x: x and "comment__CommentText" in x)
    for tag in comment_tags:
        reviews.append(tag.get_text(separator=" ", strip=True))
        
    print(f"\n[성공!] 총 {len(reviews)} 개의 리뷰를 추출했습니다.")
    for idx, r in enumerate(reviews[:3]):
        print(f" - 리뷰 {idx+1}: {r[:50]}...")

if __name__ == "__main__":
    with sync_playwright() as playwright:
        scrape_product(playwright, "https://tour.yanolja.com/package/products/ASVNS09700")
