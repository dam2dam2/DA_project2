import requests
import json

url = "https://www.airportal.go.kr/stats/transport/getDetailedAirTransportStats3.do"
headers = {
    "Content-Type": "application/json;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.airportal.go.kr/stats/transport/chartDetail3.do",
}


def test_payload(payload_name, payload_data):
    print(f"\n--- Testing: {payload_name} ---")
    try:
        res = requests.post(url, json=payload_data, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            content = data.get("content", [])
            print(f"Status: 200, Content count: {len(content)}")
            if content:
                print(
                    f"First 2 items code_name: {[c.get('code_name') for c in content[:2]]}"
                )
                # print(json.dumps(content[0], indent=2, ensure_ascii=False))
        else:
            print(f"Error: {res.status_code}")
    except Exception as e:
        print(f"Exception: {e}")


base_payload = {
    "last_yearmonth": "202401",
    "this_yearmonth": "202401",
    "sn_gubun": "0",
    "airport_gubun": "ICN",
    "pass_gubun": "1",
    "carge_gubun": "2",
    "di_gubun": "I",
    "arvl_type": "total",
}

# Variations for forreign_airport_gubun
for val in ["total", "ALL", "", "region", "nation", "airport", "0", "1"]:
    p = base_payload.copy()
    p["forreign_airport_gubun"] = val
    test_payload(f"forreign_airport_gubun={val}", p)

# Variations for airport_gubun
for val in ["total", "ALL", ""]:
    p = base_payload.copy()
    p["airport_gubun"] = val
    p["forreign_airport_gubun"] = "total"
    test_payload(f"airport_gubun={val}, forreign_airport_gubun=total", p)

# Maybe sn_gubun needs to be wider?
p = base_payload.copy()
p["sn_gubun"] = "total"
test_payload("sn_gubun=total", p)
