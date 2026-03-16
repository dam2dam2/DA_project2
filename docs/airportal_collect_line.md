## 1) HTTP 요청정보와 헤더

Request URL
https://www.airportal.go.kr/stats/transport/getDetailedAirTransportStats3.do
Request Method
POST
Status Code
200 OK
Remote Address
27.101.233.66:443
Referrer Policy
strict-origin-when-cross-origin
cache-control
no-cache, no-store, max-age=0, must-revalidate
connection
Keep-Alive
content-type
application/json
date
Sat, 14 Mar 2026 07:30:05 GMT
expires
0
keep-alive
timeout=5, max=99
pragma
no-cache
server
Apache
strict-transport-security
max-age=31536000 ; includeSubDomains
transfer-encoding
chunked
x-content-type-options
nosniff
x-frame-options
DENY
x-xss-protection
1; mode=block
accept
application/json, text/javascript, _/_; q=0.01
accept-encoding
gzip, deflate, br, zstd
accept-language
ko,en-US;q=0.9,en;q=0.8,ja;q=0.7
authorization
null
connection
keep-alive
content-length
193
content-type
application/json;charset=UTF-8
cookie
WMONID=MyWz1uZzNtu; JSESSIONID=Y05ek72uOupoEWe-2XwtRoltJwjBxE-bXgFValDU.kca20
dnt
1
host
www.airportal.go.kr
origin
https://www.airportal.go.kr
referer
https://www.airportal.go.kr/stats/transport/chartDetail3.do
request-call
web-rest
sec-ch-ua
"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"
sec-ch-ua-mobile
?0
sec-ch-ua-platform
"macOS"
sec-fetch-dest
empty
sec-fetch-mode
cors
sec-fetch-site
same-origin
user-agent
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
x-requested-with
XMLHttpRequest

## 2) Payload 정보

{"last_yearmonth":"201802","this_yearmonth":"201802","sn_gubun":"0","airport_gubun":"ICN","pass_gubun":"1","carge_gubun":"2","forreign_airport_gubun":"total","di_gubun":"I","arvl_type":"total"}

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```
{
    "requestMethod": "POST",
    "path": "/stats/transport/getDetailedAirTransportStats3.do",
    "content": [
        {
            "last_yearmonth": null,
            "this_yearmonth": null,
            "sn_gubun": null,
            "airport_gubun": null,
            "forreign_airport_gubun": null,
            "pass_gubun": null,
            "carge_gubun": null,
            "di_gubun": null,
            "pyn_gubun": null,
            "arvl_type": null,
            "code_name": "전체 합계",
            "airport_name": null,
            "pass": "4550037",
            "cargo": "76969",
            "flight_cnt": "28047"
        },
```

## 4) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장하기
