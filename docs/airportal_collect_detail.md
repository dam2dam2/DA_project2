## 1) HTTP 요청정보와 헤더

Request URL
https://www.airportal.go.kr/stats/transport/getDetailedAirTransportStats4.do
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
Thu, 12 Mar 2026 11:31:13 GMT
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
126
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
https://www.airportal.go.kr/stats/transport/chartDetail4.do
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

- 정기-유임여객-출발
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"0","pass_gubun":"1","arvl_type":"D","carge_gubun":"2"}
- 부정기-유임여객-출발
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"1","pass_gubun":"1","arvl_type":"D","carge_gubun":"2"}
- 정기-유임여객-도착
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"0","pass_gubun":"1","arvl_type":"A","carge_gubun":"2"}
- 부정기-유임여객-도착
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"1","pass_gubun":"1","arvl_type":"A","carge_gubun":"2"}
- 정기-환승여객-도착
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"0","pass_gubun":"3","arvl_type":"A","carge_gubun":"2"}
- 부정기-환승여객-도착
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"1","pass_gubun":"3","arvl_type":"A","carge_gubun":"2"}
- 정기-환승여객-출발
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"0","pass_gubun":"3","arvl_type":"D","carge_gubun":"2"}
- 부정기-환승여객-출발
  {"last_yearmonth":"202602","this_yearmonth":"202602","sn_gubun":"1","pass_gubun":"3","arvl_type":"D","carge_gubun":"2"}

## 3) 응답의 일부를 Response 에서 일부를 복사해서 넣어주기 (전체는 토큰 수 제한으로 어렵습니다.)

```
{
    "requestMethod": "POST",
    "path": "/stats/transport/getDetailedAirTransportStats4.do",
    "content": [
        {
            "last_yearmonth": null,
            "this_yearmonth": null,
            "sn_gubun": null,
            "pass_gubun": null,
            "carge_gubun": null,
            "area_gubun": null,
            "arvl_type": null,
            "nation_gubun": null,
            "nation_code": "",
            "area_code": "",
            "area_name": "전체 합계",
            "area_listorder": "0",
            "nation_name": "",
            "pass": "2130",
            "cargo": "1376",
            "nation_code_b": "총계",
            "flight_cnt": "834"
        }
```

## 4) 한페이지가 성공적으로 수집되는지 확인하고 csv 파일로 저장하기
