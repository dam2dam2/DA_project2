"""
야놀자 투어 다낭/나트랑 패키지 상품 리뷰 전체 수집 스크립트

[수집 흐름]
1단계: Playwright로 검색 페이지를 열어 내부 queryId를 캡처하고,
       해당 queryId로 API를 페이징하며 전체 상품 목록을 수집합니다.
2단계: 각 상품 상세 페이지에서 '더보기' 버튼을 끝까지 반복 클릭하여 모든 리뷰 수집
3단계: 수집된 데이터를 CSV 파일로 저장

[저장 위치]
data/reviews_danang_nhatrang.csv
"""

import requests
import time
import csv
import os
from urllib.parse import quote, urlencode
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# ─────────────────────────────────────────────
# 설정값
# ─────────────────────────────────────────────

# 수집할 지역 검색어 목록
SEARCH_QUERIES = ["다낭", "나트랑"]

# 상품 목록 검색 API 기본 URL
SEARCH_API_BASE = "https://tour.yanolja.com/tour-api/package-hub/search"

# 검색 API 요청 헤더 (브라우저로 위장)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "accept": "*/*",
    "accept-language": "ko,en-US;q=0.9,en;q=0.8",
    "nol-service": "yanolja",
}

# 결과 저장 경로
OUTPUT_CSV = "/Users/dami/innercircle/DA_project2/data/reviews_danang_nhatrang.csv"

# 페이지당 상품 수
PAGE_SIZE = 20

# 더보기 버튼 클릭 최대 횟수 (1회 클릭 시 리뷰 약 5개 추가 / 300개 = 60번)
MAX_CLICKS = 70


# ─────────────────────────────────────────────
# 1단계-A: Playwright로 queryId 캡처
# ─────────────────────────────────────────────

def get_query_id_via_browser(playwright_page, query: str) -> str | None:
    """
    Playwright 브라우저로 야놀자 패키지 검색 페이지를 열어,
    내부 API 호출에서 사용되는 queryId를 캡처합니다.
    야놀자는 검색 시 세션별로 queryId를 동적 생성하므로 브라우저 방식이 필요합니다.
    """
    captured_query_id = None

    def on_response(response):
        nonlocal captured_query_id
        if captured_query_id:
            return
        url = response.url
        # 상품 목록 검색 API 응답에서 queryId 추출
        if "package-hub/search" in url:
            try:
                data = response.json()
                qid = data.get("queryId", "")
                if qid:
                    captured_query_id = qid
            except Exception:
                pass

    playwright_page.on("response", on_response)
    search_url = f"https://tour.yanolja.com/package-search?query={quote(query)}&page=1"
    print(f"  [{query}] 검색 페이지 접속하여 queryId 캡처 중...")
    try:
        playwright_page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
    except Exception:
        pass
    playwright_page.wait_for_timeout(3000)
    playwright_page.remove_listener("response", on_response)

    if captured_query_id:
        print(f"  [{query}] queryId 캡처 성공: {captured_query_id}")
    else:
        print(f"  [{query}] ⚠ queryId 캡처 실패")
    return captured_query_id


# ─────────────────────────────────────────────
# 1단계-B: 상품 목록 API 페이징 수집
# ─────────────────────────────────────────────

def collect_product_ids(query: str, query_id: str) -> list[dict]:
    """
    캡처한 queryId를 사용하여 검색 API를 순회하며 전체 상품 목록을 반환합니다.
    """
    products = []
    page = 1

    while True:
        param_dict = {"queryId": query_id, "page": page, "pageSize": PAGE_SIZE}
        full_url = f"{SEARCH_API_BASE}?{urlencode(param_dict)}"
        referer_url = f"https://tour.yanolja.com/package-search?query={quote(query)}&page={page}"

        try:
            res = requests.get(
                full_url,
                headers={**HEADERS, "referer": referer_url},
            )
            data = res.json()
        except Exception as e:
            print(f"  [{query}] API 오류 (page={page}):", e)
            break

        page_info = data.get("page", {})
        docs = data.get("documents", [])

        if not docs:
            break

        for doc in docs:
            pid = doc.get("id", "")
            name = doc.get("name", "")
            review_count = doc.get("review", {}).get("count", 0)
            review_score = doc.get("review", {}).get("score", 0)
            product_url = f"https://tour.yanolja.com/package/products/{pid}"
            products.append({
                "id": pid,
                "name": name,
                "review_count": review_count,
                "review_score": review_score,
                "url": product_url,
                "query": query,
            })

        max_page = page_info.get("maxPage", 1)
        print(f"  [{query}] page {page}/{max_page} 수집 완료 ({len(docs)}개)")

        if page >= max_page:
            break
        page += 1
        time.sleep(0.5)

    return products


# ─────────────────────────────────────────────
# 2단계: 상품별 리뷰 수집 (Playwright DOM 크롤링)
# ─────────────────────────────────────────────

def scrape_reviews_for_product(page, product: dict) -> list[dict]:
    """
    Playwright page 객체를 받아, 해당 상품 URL에 접속한 뒤
    '더보기' 버튼을 끝까지 클릭하며 모든 리뷰를 수집합니다.
    """
    url = product["url"]
    pid = product["id"]
    name = product["name"]
    print(f"\n  ▶ [{pid}] {name[:35]}... (예상 리뷰: {product['review_count']}개)")

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=25000)
    except Exception as e:
        print(f"    ⚠ 접속 오류(계속 진행): {e}")

    # 리뷰 영역이 하단에 있으므로 스크롤로 로딩 유도
    for _ in range(5):
        page.evaluate("window.scrollBy(0, 1200)")
        page.wait_for_timeout(600)

    # '더보기' 버튼이 사라질 때까지 반복 클릭
    # 사용자 제공 HTML에서 확인된 리뷰 전용 더보기 버튼의 클래스명: more-button___StyledButton
    clicks = 0
    while clicks < MAX_CLICKS:
        try:
            # 1순위: 리뷰 전용 더보기 버튼 (클래스명으로 정확히 특정)
            btn = page.locator("button[class*='more-button___StyledButton']").first
            if btn.count() == 0 or not btn.is_visible(timeout=2000):
                # 2순위: 리뷰 더보기 텍스트 포함 버튼
                btn = page.locator("button:has-text('리뷰 더보기')").first
                if btn.count() == 0 or not btn.is_visible(timeout=2000):
                    break
            btn.evaluate("node => node.click()")
            clicks += 1
            page.wait_for_timeout(1200)
        except Exception:
            break

    print(f"    더보기 {clicks}회 클릭 완료. HTML 파싱 중...")

    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    review_items = soup.find_all("li", recursive=True)
    collected = []

    for item in review_items:
        # 리뷰 텍스트 파싱 (class명 부분 일치 방식)
        comment_tag = item.find("p", class_=lambda c: c and "comment__CommentText" in c)
        if not comment_tag:
            continue
        text = comment_tag.get_text(separator=" ", strip=True)

        # 별점: 별 아이콘(span) 개수로 산정
        star_container = item.find("div", class_=lambda c: c and "star-rating" in c)
        star = len(star_container.find_all("span")) if star_container else 0

        # 작성자명
        author_tag = item.find("p", class_=lambda c: c and "user-metadata___StyledText" in c)
        author = author_tag.get_text(strip=True) if author_tag else ""

        # 작성일
        date_str = ""
        if author_tag:
            siblings = list(author_tag.parent.find_all("p"))
            if len(siblings) >= 2:
                date_str = siblings[1].get_text(strip=True)

        collected.append({
            "상품ID": pid,
            "상품명": name,
            "지역": product["query"],
            "별점": star,
            "작성자": author,
            "작성일": date_str,
            "리뷰내용": text,
        })

    print(f"    ✅ 수집 완료: {len(collected)}개")
    return collected


# ─────────────────────────────────────────────
# 3단계: 전체 실행 및 CSV 저장
# ─────────────────────────────────────────────

def save_csv(reviews: list[dict], path: str):
    """리뷰 목록을 CSV 파일로 저장합니다."""
    if not reviews:
        return
    fieldnames = ["상품ID", "상품명", "지역", "별점", "작성자", "작성일", "리뷰내용"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(reviews)


def main():
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    all_products = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        # ─── 1단계: 다낭/나트랑 상품 목록 수집 ───
        for query in SEARCH_QUERIES:
            print(f"\n========== [{query}] 상품 목록 수집 시작 ==========")
            # Playwright로 검색 페이지를 열어 queryId 캡처
            query_id = get_query_id_via_browser(page, query)
            if not query_id:
                print(f"  [{query}] queryId 획득 실패로 건너뜁니다.")
                continue
            # 캡처된 queryId로 API 페이징하며 상품 목록 수집
            products = collect_product_ids(query, query_id)
            print(f"  [{query}] 총 상품 수: {len(products)}개")
            all_products.extend(products)

        # 리뷰 1개 이상 & 중복 제거
        seen_ids = set()
        unique_products = []
        for p in all_products:
            if p["review_count"] > 0 and p["id"] not in seen_ids:
                seen_ids.add(p["id"])
                unique_products.append(p)

        print(f"\n전체 상품: {len(all_products)}개 → 리뷰 있는 고유 상품: {len(unique_products)}개\n")

        # ─── 2단계: 각 상품의 리뷰 수집 ───
        all_reviews = []
        for idx, product in enumerate(unique_products, 1):
            print(f"[{idx}/{len(unique_products)}] 처리 중...")
            reviews = scrape_reviews_for_product(page, product)
            all_reviews.extend(reviews)
            # 5개 상품 처리마다 중간 저장 (중단 대비)
            if idx % 5 == 0:
                save_csv(all_reviews, OUTPUT_CSV)
                print(f"  ▷ 중간 저장 (현재까지 총 {len(all_reviews)}개 리뷰)")
            time.sleep(1.0)

        browser.close()

    # ─── 3단계: 최종 저장 ───
    save_csv(all_reviews, OUTPUT_CSV)
    print(f"\n🎉 수집 완료! 총 {len(all_reviews)}개 리뷰 저장: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
