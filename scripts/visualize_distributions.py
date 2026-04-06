import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os

# 파일 경로 설정
INPUT_PATH = "/Users/dami/innercircle/DA_project2/data/eda_results/reviews_with_details.csv"
OUTPUT_DIR = "/Users/dami/innercircle/DA_project2/data/eda_results"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def visualize_distributions():
    # 1. 데이터 로드
    df = pd.read_csv(INPUT_PATH, encoding="utf-8-sig")
    
    # 리뷰 수가 많은 상위 7개 상품 선정 (시각화 가독성 위해)
    top_products = df['상품명'].value_counts().head(7).index.tolist()
    df_top = df[df['상품명'].isin(top_products)].copy()
    
    # 짧은 상품명 생성 (그래프 표시용)
    df_top['short_name'] = df_top['상품명'].apply(lambda x: (x[:15] + '..') if len(x) > 15 else x)

    def plot_distribution(column_name, title, filename):
        # 파이프(|) 구분자 분리 및 확장 (Explode)
        expanded = df_top.assign(temp=df_top[column_name].str.split('|')).explode('temp')
        expanded = expanded[expanded['temp'] != '정보없음'] # 정보없음 제외
        
        if expanded.empty:
            print(f"⚠ {column_name}에 대한 유효한 데이터가 없습니다.")
            return

        # 상품별 태그 빈도 집계 (교차 테이블 생성)
        dist = pd.crosstab(expanded['short_name'], expanded['temp'], normalize='index') * 100
        
        # 시각화
        ax = dist.plot(kind='barh', stacked=True, figsize=(14, 8), colormap='Set3')
        plt.title(f"{title} (상위 리뷰 상품)", fontsize=16, pad=20)
        plt.xlabel("비중 (%)", fontsize=12)
        plt.ylabel("상품명 (샘플)", fontsize=12)
        plt.legend(title=column_name, bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 각 바 중앙에 텍스트 표시
        for p in ax.patches:
            width, height = p.get_width(), p.get_height()
            if width > 5: # 5% 이상의 비중만 텍스트 표시
                x, y = p.get_xy() 
                ax.text(x + width/2, y + height/2, f'{width:.1f}%', 
                        horizontalalignment='center', verticalalignment='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, filename))
        plt.close()
        print(f"✅ {filename} 생성 완료")

    # 2. 동행유형 분포 시각화
    plot_distribution('동행유형', '상품별 동행자 유형 분포', 'dist_companion.png')
    
    # 3. 연령/특이사항 분포 시각화
    plot_distribution('연령/특이사항', '상품별 연령 및 특이사항 분포', 'dist_age_context.png')

if __name__ == "__main__":
    visualize_distributions()
