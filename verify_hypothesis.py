import pandas as pd
import numpy as np

# 1. 데이터 로드
reviews_path = '/Users/dami/innercircle/DA_project2/hanatour_sentiment_result.csv'
packages_path = '/Users/dami/innercircle/DA_project2/data/packages_nol.csv'

reviews = pd.read_csv(reviews_path, encoding='utf-8-sig')
# packages_nol.csv는 헤더가 없거나 다를 수 있으므로 컬럼명을 수동 지정 (샘플 확인 결과 기반)
packages = pd.read_csv(packages_path, encoding='utf-8-sig', names=['destination', '상품코드', 'title', 'tags', 'type', 'category', 'date', 'price', 'discount_price', 'airline', 'duration', 'review_count', 'score', 'unknown', 'class'], header=None)

# 2. 데이터 전처리
reviews.columns = [col.replace('\ufeff', '') for col in reviews.columns]
packages.columns = [col.replace('\ufeff', '') for col in packages.columns]

# 상품코드로 병합 (패키지 중복 제거)
packages_clean = packages[['상품코드', 'discount_price']].drop_duplicates('상품코드')
merged = pd.merge(reviews, packages_clean, on='상품코드', how='inner')

# 3. 변수 생성
# 쇼핑 유무 필터링 (명시적 '노쇼핑' 키워드가 없으면 쇼핑 있는 것으로 간주)
def check_shopping(title):
    title = str(title)
    if any(k in title for k in ['노쇼핑', 'NO쇼핑', 'NO옵션', '노옵션', '노팁']):
        return 'No Shopping'
    return 'With Shopping'

merged['is_shopping'] = merged['상품명'].apply(check_shopping)

# 가격을 숫자로 변환 (콤마 제거 등)
merged['discount_price'] = pd.to_numeric(merged['discount_price'], errors='coerce')
merged = merged.dropna(subset=['discount_price'])

# 가격 그룹 (Low, Mid, High) - 3분위수 기준
q1 = merged['discount_price'].quantile(0.33)
q2 = merged['discount_price'].quantile(0.66)

def get_price_group(price):
    if price <= q1: return 'Low'
    if price <= q2: return 'Mid'
    return 'High'

merged['price_group'] = merged['discount_price'].apply(get_price_group)

# 4. 가설 검증 분석 (평균 평점)
analysis = merged.groupby(['price_group', 'is_shopping'])['평점'].agg(['mean', 'count']).unstack()

print("=== 가격 및 쇼핑 유무별 평균 평점 교차 분석 ===")
print(analysis)

# 5. 가설 검증 공식화
# 하락폭 = (No Shopping 평균 평점) - (With Shopping 평균 평점)
high_drop = analysis.loc['High', ('mean', 'No Shopping')] - analysis.loc['High', ('mean', 'With Shopping')]
low_drop = analysis.loc['Low', ('mean', 'No Shopping')] - analysis.loc['Low', ('mean', 'With Shopping')]

print(f"\n고가 상품군에서의 평점 하락폭: {high_drop:.4f}")
print(f"저가 상품군에서의 평점 하락폭: {low_drop:.4f}")

if high_drop > low_drop:
    print("\n[결론] 가설이 지지됩니다: 고가 상품일수록 쇼핑 포함에 따른 고객 불만(평점 하락)이 더 큽니다.")
else:
    print("\n[결론] 가설이 지지되지 않습니다.")

# 6. 결과 저장
analysis.to_csv('/Users/dami/innercircle/DA_project2/hypothesis_summary.csv')
merged.to_csv('/Users/dami/innercircle/DA_project2/hypothesis_full_data.csv', index=False, encoding='utf-8-sig')
