import pandas as pd
import re
import os

# 파일 경로 설정
CSV_PATH = "/Users/dami/innercircle/DA_project2/data/reviews_danang_nhatrang.csv"
OUTPUT_DIR = "/Users/dami/innercircle/DA_project2/data/eda_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_details():
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    
    # 1. 여행 기간 추출 (Regex)
    def get_duration(text):
        match = re.search(r'(\d+)박\s*(\d+)일', str(text))
        if match:
            return f"{match.group(1)}박{match.group(2)}일"
        return "정보없음"

    # 2. 동행자 분석 (Keywords)
    companion_keywords = {
        "가족(부모동반)": ["부모", "엄마", "아빠", "시어머니", "시아버지", "장인", "장모", "어르신", "고령"],
        "가족(자녀동반)": ["아이", "딸", "아들", "손자", "손주", "애들", "초등학생", "중학생", "고등학생", "사춘기", "조카"],
        "부부/커플": ["부부", "남편", "아내", "신혼", "와이프", "커플"],
        "친구/지인": ["친구", "동생", "언니", "자매", "지인", "동료"]
    }

    def get_companion(text):
        found = []
        for cat, keywords in companion_keywords.items():
            if any(kw in str(text) for kw in keywords):
                found.append(cat)
        return "|".join(found) if found else "정보없음"

    # 3. 연령/생애주기 특이사항 (Age & Occasion)
    age_keywords = {
        "기념여행(환갑/칠순 등)": ["환갑", "칠순", "팔순", "생신", "기념", "축하"],
        "아이동반": ["아이", "초등학생", "유치원", "손주", "손자"],
        "고령층": ["고령", "어르신", "팔십", "칠십", "휠체어"]
    }

    def get_age_context(text):
        found = []
        for cat, keywords in age_keywords.items():
            if any(kw in str(text) for kw in keywords):
                found.append(cat)
        return "|".join(found) if found else "정보없음"

    # 데이터 추출 적용 (리뷰내용 + 상품명 결합하여 검색)
    df['search_text'] = df['상품명'] + " " + df['리뷰내용'].fillna('')
    df['여행기간'] = df['search_text'].apply(get_duration)
    df['동행유형'] = df['search_text'].apply(get_companion)
    df['연령/특이사항'] = df['search_text'].apply(get_age_context)

    # 4. 상품별 집계
    # 상품별로 가장 많이 나타나는 기간, 동행유형, 특이사항을 요약합니다.
    summary = df.groupby(['상품ID', '상품명']).agg({
        '리뷰내용': 'count',
        '여행기간': lambda x: x.value_counts().index[0] if x.value_counts().index[0] != '정보없음' or len(x.value_counts()) == 1 else x.value_counts().index[1],
        '동행유형': lambda x: ", ".join(x.unique() if '정보없음' not in x.unique() or len(x.unique()) == 1 else [v for v in x.unique() if v != '정보없음']),
        '연령/특이사항': lambda x: ", ".join(x.unique() if '정보없음' not in x.unique() or len(x.unique()) == 1 else [v for v in x.unique() if v != '정보없음'])
    }).reset_index()

    summary.columns = ['상품ID', '상품명', '리뷰수', '주요기간', '동행유형', '연령/특이사항']
    
    # 결과 출력
    print("### [심화 분석] 상품별 사용자 특성 요약")
    print(summary[['상품ID', '상품명', '리뷰수', '주요기간', '동행유형']].head(10).to_string(index=False))
    
    # 결과를 CSV로 저장
    summary.to_csv(os.path.join(OUTPUT_DIR, "product_user_analysis.csv"), index=False, encoding="utf-8-sig")
    df.to_csv(os.path.join(OUTPUT_DIR, "reviews_with_details.csv"), index=False, encoding="utf-8-sig")
    
    print(f"\n✅ 분석 완료! 결과 저장: {os.path.join(OUTPUT_DIR, 'product_user_analysis.csv')}")

if __name__ == "__main__":
    extract_details()
