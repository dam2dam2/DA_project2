import requests
import json
import os
import time

def collect_instagram_hashtags():
    # API 설정 정보 (docs/instagram.md 기반)
    # 실제 환경에서는 보안을 위해 환경 변수 등을 사용하는 것이 좋으나,
    # 사용자가 제공한 파일의 정보를 우선적으로 활용합니다.
    ACCESS_TOKEN = "EAAMZBM2y3UqsBQ7zVoUyRHzoXcVAyx4gDekIPxWELbZCWZBrmeqd5zh6nncfHZCAZBG0oCyHGKDUHkztPY7y4A4fWZCrJ3eqf2MWZA1AnKd6UPhIra87Bn1Osp0XgnZBky2ZAkIYimPZAUAlwShWTKWQMfrgxuCogMBvmZB7y222M8COImOZAJuwouO6iLqMZAbPTSN2WbmXK18ZB4V2WQsyQKPxqIG0Fv1q43ICe12QZCZBKlZCBOOtiMWrZCAdAha3RerjZAfraj1e9j9sOx2Lrgs43EZD"
    INSTA_BUSINESS_ID = "25872153309123227"
    
    BASE_URL = "https://graph.facebook.com/v25.0"
    
    # 수집할 해시태그 목록
    hashtags = ["여행", "여행스타그램", "travel", "trip"]
    all_data = []

    print(f"--- 인스타그램 데이터 수집 시작 (해시태그: {', '.join(hashtags)}) ---")

    for tag_name in hashtags:
        try:
            # 1. 해시태그 ID 조회
            search_url = f"{BASE_URL}/ig_hashtag_search"
            params = {
                "user_id": INSTA_BUSINESS_ID,
                "q": tag_name,
                "access_token": ACCESS_TOKEN
            }
            response = requests.get(search_url, params=params)
            res_data = response.json()
            
            if "data" not in res_data or not res_data["data"]:
                print(f"❌ '{tag_name}' 해시태그를 찾을 수 없습니다: {res_data}")
                continue
                
            hashtag_id = res_data["data"][0]["id"]
            print(f"✅ '{tag_name}' (ID: {hashtag_id}) 수집 중...")

            # 2. 최근 미디어 수집 (recent_media)
            media_url = f"{BASE_URL}/{hashtag_id}/recent_media"
            media_params = {
                "user_id": INSTA_BUSINESS_ID,
                "fields": "id,media_type,media_url,permalink,caption,timestamp,like_count,comments_count",
                "access_token": ACCESS_TOKEN,
                "limit": 20  # 태그당 최근 20개 수집
            }
            media_res = requests.get(media_url, params=media_params)
            media_data = media_res.json()

            if "data" in media_data:
                for item in media_data["data"]:
                    item["search_hashtag"] = tag_name
                    all_data.append(item)
                print(f"   ㄴ {len(media_data['data'])}개의 게시물 수집 완료.")
            else:
                print(f"   ㄴ ⚠️ 게시물을 불러올 수 없습니다: {media_data}")

            # API 속도 제한 고려
            time.sleep(1)

        except Exception as e:
            print(f"❌ '{tag_name}' 처리 중 오류 발생: {e}")

    # 3. 결과 저장
    SAVE_PATH = "data/instagram_travel_data.json"
    os.makedirs("data", exist_ok=True)
    
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)

    print(f"\n--- 수집 완료! 총 {len(all_data)}개 데이터 저장됨: {SAVE_PATH} ---")

if __name__ == "__main__":
    collect_instagram_hashtags()
