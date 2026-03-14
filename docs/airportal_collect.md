## 1) HTTP 요청정보와 헤더

Request URL
https://www.airportal.go.kr/stats/transport/getDailyAirTransportStats.do
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
Thu, 12 Mar 2026 11:13:10 GMT
expires
0
keep-alive
timeout=5, max=84
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
41
content-type
application/json;charset=UTF-8
cookie
WMONID=MyWz1uZzNtu; JSESSIONID=WdzV_gsw2fa-8LUmiHcAQMmjmWEM4uJORHWRb5gD.kca20
dnt
1
host
www.airportal.go.kr
origin
https://www.airportal.go.kr
referer
https://www.airportal.go.kr/stats/transport/liveAirplane.do
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

{"startDt":"20260203","endDt":"20260305"}

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```
{
    "requestMethod": "POST",
    "path": "/stats/transport/getDailyAirTransportStats.do",
    "content": [
        {
            "startDt": null,
            "endDt": null,
            "ap_icao": "인천공항",
            "int_dom_cls": "국제선",
            "dep_sch_cnt": "19064",
            "dep_cnt": "18701",
            "dep_cnl_cnt": "253",
            "arr_sch_cnt": "19065",
            "arr_cnt": "18679",
            "arr_cnl_cnt": "238"
        }
```

## 4) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장하기

---

## 1) HTTP 요청정보와 헤더

Request URL
https://www.airportal.go.kr/stats/transport/selectDailyStatisticsByRoute.do
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
Thu, 12 Mar 2026 11:20:45 GMT
expires
0
keep-alive
timeout=5, max=100
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
81
content-type
application/json;charset=UTF-8
cookie
WMONID=MyWz1uZzNtu; JSESSIONID=WdzV_gsw2fa-8LUmiHcAQMmjmWEM4uJORHWRb5gD.kca20
dnt
1
host
www.airportal.go.kr
origin
https://www.airportal.go.kr
referer
https://www.airportal.go.kr/stats/transport/dailyRoute.do
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

{"startDt":"20260203","endDt":"20260305","koreaAirport":"RKSI","airlineType":"I"}
{"startDt":"20260203","endDt":"20260305","koreaAirport":"RKSI","airlineType":"D"}

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```
{
    "requestMethod": "POST",
    "path": "/stats/transport/selectDailyStatisticsByRoute.do",
    "content": [
        {
            "startDt": null,
            "endDt": null,
            "airlineType": null,
            "koreaAirport": null,
            "ap1": "인천 (RKSI)",
            "ap2": " (KBAD)",
            "arr_FP": "1",
            "dep_FP": "0",
            "total_FP": "1",
            "dep_PERSON": "0",
            "arr_PERSON": "0",
            "arr_WEIGHT": "0",
            "dep_WEIGHT": "0",
            "total_PERSON": "0",
            "total_WEIGHT": "0",
            "al_ICAO": "GTI",
            "ap_ROUTE": "KBAD"
        },
```

## 4) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장하기
