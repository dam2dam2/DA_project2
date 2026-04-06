import pandas as pd
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import numpy as np

# 1. 데이터 로드
file_path = '/Users/dami/innercircle/DA_project2/hanatour_reviews.csv'
df = pd.read_csv(file_path, encoding='utf-8-sig')

# 2. 감성 분석 모델 설정 (PyTorch 기반 KoELECTRA NSMC 최신 공개 모델)
model_name = "daekeun-ml/koelectra-small-v3-nsmc"
classifier = pipeline("sentiment-analysis", model=model_name, framework="pt")

# 3. 분석 수행 (리뷰 내용이 있는 것만)
df = df.dropna(subset=['내용'])
texts = df['내용'].astype(str).tolist()

print(f"총 {len(texts)}건의 리뷰에 대해 감성 분석을 시작합니다...")

# 대량 데이터 처리를 위해 배치 단위로 실행하거나 리스트 컴프리헨션 사용
results = []
# 텍스트가 너무 길 경우 절단 처리 포함
batch_size = 32
for i in range(0, len(texts), batch_size):
    batch_texts = [text[:512] for text in texts[i:i + batch_size]]
    batch_results = classifier(batch_texts)
    results.extend(batch_results)

# 5. 결과 가공
df['sentiment_label'] = [res['label'] for res in results]
df['sentiment_score'] = [res['score'] for res in results]

# 레이블 한글화 (예: LABEL_1 -> 긍정, LABEL_0 -> 부정)
# 모델에 따라 다를 수 있으므로 확인이 필요하지만, 대개 NSMC 모델은 1이 긍정
df['label_korean'] = df['sentiment_label'].apply(lambda x: '긍정' if '1' in x or 'pos' in x.lower() else '부정')

# 6. 결과 저장
output_path = '/Users/dami/innercircle/DA_project2/hanatour_sentiment_result.csv'
df.to_csv(output_path, index=False, encoding='utf-8-sig')

print(f"분석 완료! 결과가 저장되었습니다: {output_path}")

#7. 간단 요약 출력
summary = df['label_korean'].value_counts()
print("\n[감성 분석 요약]")
print(summary)
