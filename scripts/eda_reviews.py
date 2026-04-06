import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import re

# 파일 경로 설정
CSV_PATH = "/Users/dami/innercircle/DA_project2/data/reviews_danang_nhatrang.csv"
OUTPUT_DIR = "/Users/dami/innercircle/DA_project2/data/eda_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def perform_eda():
    # 1. 데이터 로드 (UTF-8-SIG 고려)
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    
    print("### [1] 기본 데이터 정보")
    print(df.info())
    print("\n### [2] 별점 통계")
    print(df['별점'].describe())
    
    # 2. 기초 통계 시각화 (별점 분포)
    plt.figure(figsize=(10, 6))
    df['별점'].value_counts().sort_index().plot(kind='bar', color='skyblue')
    plt.title("리뷰 별점 분포")
    plt.xlabel("별점")
    plt.ylabel("리뷰 수")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "star_distribution.png"))
    plt.close()

    # 3. TF-IDF 분석
    # 형태소 분석기 없이 정규식을 이용해 한글 단어(2글자 이상)만 추출하는 토크나이저 설정
    def simple_tokenizer(text):
        return re.findall(r'[가-힣]{2,}', str(text))

    tfidf = TfidfVectorizer(tokenizer=simple_tokenizer, min_df=2, max_df=0.9)
    tfidf_matrix = tfidf.fit_transform(df['리뷰내용'].fillna(''))
    
    # 상위 30개 단어 빈도(TF-IDF 합계) 계산
    words = tfidf.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    word_freq = pd.DataFrame({'word': words, 'tfidf_sum': tfidf_sums})
    top_30_words = word_freq.sort_values(by='tfidf_sum', ascending=False).head(30)
    
    print("\n### [3] TF-IDF 상위 30개 단어")
    print(top_30_words.to_string(index=False))
    
    # 상위 30개 단어 시각화
    plt.figure(figsize=(12, 8))
    plt.barh(top_30_words['word'][::-1], top_30_words['tfidf_sum'][::-1], color='coral')
    plt.title("TF-IDF 기반 상위 30개 핵심 키워드")
    plt.xlabel("TF-IDF Score Sum")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "top_30_keywords.png"))
    plt.close()

    # 4. TF-IDF 히트맵 (상위 10개 행, 상위 50개 열)
    # 상위 50개 특징(단어) 선정
    top_50_indices = tfidf_sums.argsort()[-50:][::-1]
    top_50_words = [words[i] for i in top_50_indices]
    
    # 상위 10개 행, 상위 50개 열 슬라이싱
    subset_matrix = tfidf_matrix[:10, top_50_indices].toarray()
    
    print("\n### [4] TF-IDF 상위 10개 행 x 50개 열 행렬 (일부)")
    subset_df = pd.DataFrame(subset_matrix, columns=top_50_words)
    print(subset_df.iloc[:, :10].to_string()) # 테이블 출력은 너무 길어질 수 있으므로 샘플링해서 보여줌
    
    # 히트맵 시각화
    plt.figure(figsize=(20, 10))
    plt.imshow(subset_matrix, cmap='YlOrRd', aspect='auto')
    plt.colorbar(label='TF-IDF Score')
    plt.xticks(range(len(top_50_words)), top_50_words, rotation=90)
    plt.yticks(range(10), [f"Doc {i+1}" for i in range(10)])
    plt.title("TF-IDF Score Heatmap (Top 10 Docs x Top 50 Words)")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "tfidf_heatmap.png"))
    plt.close()
    
    # 히트맵 데이터를 CSV로도 저장 (추후 테이블 출력용)
    subset_df.to_csv(os.path.join(OUTPUT_DIR, "tfidf_subset_matrix.csv"), index=False, encoding="utf-8-sig")

if __name__ == "__main__":
    perform_eda()
