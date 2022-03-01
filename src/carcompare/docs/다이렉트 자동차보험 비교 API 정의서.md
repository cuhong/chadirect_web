# 다이렉트 자동차보험 비교 API 정의서
## 문서정보
- 작성자 : ITS 개발팀
- version : 1.4
- 작성일 : 2020-10-29
- 문의 : gifox@doore.link / 010-2649-6960


## API 정의
### 접속정보
- BASE_URL : `별도요청`
- TEST URL : `별도요청`
- SAMPLE URL : `https://dadais.kr/car/compareb2b`

### 인증방식xd
- 허가된 IP (요청시 추가 및 변경 가능) or
- API-KEY 인증 방식(별도 제공)

### API 규격
#### 공통 HEADER
##### Content-Type 
- `application/x-www-form-urlencoded` or 
- `application/json`

#### 개요
| 구분 |  단계 | 설명 | URL | Request 항목 | Response 항목 | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 서비스가동 || 서비스를 가동하고 세션키 제공 | service-init/ | None | session\_id, message | 200(성공), 400(다모아 에러시), <br>500(스크래퍼 실패) |,
| 휴대폰 개인인증 |인증요청(서비스가동 미사용시)| 휴대폰 개인인증 요청을 보낸다 | phone-auth-num/ | session\_id, name,<br>ssn\_prefix, ssn\_suffix, <br>phone\_company,<br>phone1, phone2, phone3 | message | 200(성공),<br>400(다모아 에러시),<br>500(스크래퍼 실패) |,
| 휴대폰 개인인증 |인증요청(권장, 서비스가동 사용시)| 휴대폰 개인인증 요청을 보낸다 | send-auth-num/ | session\_id, name,<br>ssn\_prefix, ssn\_suffix,<br>phone\_company,<br>phone1, phone2, phone3 | message | 200(성공),<br>400(다모아 에러시),<br>500(스크래퍼 실패) |,
| 휴대폰 개인인증 |인증번호확인| 인증요청에 대한 결과를 확인 | phone-auth-check/ | session\_id, auth\_number | message | 200(성공),<br>400(다모아 에러시)<br>406(다모아 서비스 제공 불가 사용자)<br>500(스크래퍼 실패) |,
| 기존계약 확인 |기존계약 여부 및 정보 확인| 기존에 가입되어있는 자동차보험의 리스트 및 간략 정보 | expolicy-check/ | session_id | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 차종리스트 |차종리스트| 차종 구분 레벨별 실시간 리스트 제공 | get-select-carlist/ | session\_id, manufacturer,<br>register\_year, car\_name,<br>detail\_name, start\_date | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 비교결과 |최초 비교| 입력된 조건 기준에 대한 보험사별 보험료 비교 | result-list/ | session\_id, 별도탭 참조 | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 비교결과 |{회사별 세팅값 기준} 비교| 사전정의된 조건 기준에 대한 보험사별 보험료 비교 | {회사명}-list/ | session\_id, start\_date,<br>car\_no, manufacturer,<br>car\_name,  car\_register\_year,<br>detail\_car\_name, detail\_option | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 차종검색 |차종검색| 차량번호로 차종 구분을 검색 | search-carnum/ | car\_no | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 비교결과 |최초 비교| 입력된 조건 기준에 대한 보험사별 보험료 비교 | result-list/ | session\_id, 별도탭 참조 | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 비교결과 |{회사별 세팅값 기준} 비교| 사전정의된 조건 기준에 대한 보험사별 보험료 비교 | {회사명}-list/ | session\_id, start\_date,<br>car\_no, manufacturer,<br>car\_name,  car\_register\_year,<br>detail\_car\_name, detail\_option | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 비교결과 |조건변경 비교| 기준 조건 변경시 보험사별 보험료 재 비교 | recall-result/ | session\_id, 별도탭 참조 | message, data | 200(성공),<br>500(스크래퍼 실패) |,
| 서비스 연장 |세션 time_out 리뉴얼| 세션 타임아웃타임을 초기값으로 리뉴얼 | init-timeout/ | session\_id | message | 200(성공),<br>500(스크래퍼 실패) |,
| 서비스 종료 |서비스 종료| 서비스 종료 및 부여받은 세션키 및 자원 반환 | shutdown-browser/ | session\_id | message | 200(성공),<br>500(스크래퍼 실패) |,

#### API 요청 순서
- Case 1 : service-init → send-auth-num (→ expolicy-check) → result-list (→ recall-result) → shutdown-browser
- Case 2 : phone-auth-num (→ expolicy-check) → result-list (→ recall-result) → shutdown-browser
- 차종리스트 요청 : get-select-carlist 는 session_id와 무관하게 아무때나 호출 가능
- 매 단계별 5분이상 추가 요청이 없으나 서비스 유지중인 경우 init_timeout 요청 필요
- 매 단계별 고객 이탈 시 shutdown-browser 요청 요망

#### 1. 서비스 가동(POST `service-init/`)
- 서비스를 가동하고 `session_id`를 제공
- 서비스 제공 시 고객 본인인증 요청 단계에서 빠른 리턴을 위해 사전 가동 필요
- 서비스 가동 이후 `session_id`별 자원 할당 및 관리되고 있으며, 마지막 요청 이후 5분간 추가 요청이 없을시 자동 종료됨

##### 요청
```bash
curl -X "POST" "${BASE_URL}service-init/" \
     -H 'Content-Type: application/json; charset=utf-8'
```

##### 응답

응답 Status는 아래 세가지가 존재합니다.

1. 200(성공) : 정상적으로 요청에 성공하고 session-id를 발급
2. 400(실패) : 다모아 사이트에서 진행 실패
3. 500(실패) : API 서버 내 처리 실패 

###### 성공 케이스 응답(`json`)
```json
{
 "message": "Success", 
 "session_id": "f0e47b6e-76c4-46e1-bc31-2809409e7a66"  # 예시 
}
```
이후 요청에 리턴된 session_id 를 사용한다.

###### 실패(400)
다모아 사이트 진행 실패

```json
{
 "message": fail message text
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
 "message": "Fail"
}
```

#### 휴대폰 인증 요청(POST `send-auth-num/`)
- 휴대폰 본인인증 요청을 보낸다

##### 요청
```bash
curl -X "POST" "${BASE_URL}send-auth-num/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f",  # 인증번호 요청에서 수신한 `session_id`
           "name" : "홍길동",
           "ssn_prefix" : "990101",
           "ssn_suffix" : "1234567",
           "phone_company" : "01",  # 01 SKT, 02 KT, 03 LGU, 04 SKT(별정), 05 KT(별정), 06 LGU(별정),
           "phone1" : "010",
           "phone2" : "1234",
           "phone3" : "5678"
}'
```

##### 응답
###### 성공
```json
{
  "message": "Success"
}
```

###### 실패(400)
다모아 진행 실패(개인정보 상이 등)

```json
{
  "message": "휴대폰인증번호 요청오류[]↵close↵확인" # fail message text를 그대로 리턴함
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 개인 인증번호 확인(POST `phone-auth-check/`)
- 인증요청에 대한 결과를 확인

##### 요청
```bash
curl -X "POST" "${BASE_URL}send-auth-num/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f",  # 인증번호 요청에서 수신한 `session_id`
           "auth_number" : "123456"   # 고객이 입력한 인증 값 
}'
```

##### 응답
###### 성공
```json
{
  "message": "Success"
}
```

###### 실패(400)
다모아 진행 실패(인증번호 틀림 등)

```json
{
  "message": fail message text
}
```

###### 실패(406)
다모아 서비스 거부 대상(최근 4주내 갱신계약 완료자 등)

```json
{
  "message": "Deny Service"
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 기존계약 확인(POST `phone-auth-check/`)
- 기존에 가입되어있는 자동차보험의 리스트 및 간략 정보(갱신가능 여부 등)

##### 요청
```bash
curl -X "POST" "${BASE_URL}expolicy-check/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f"  # 인증번호 요청에서 수신한 `session_id`
}'
```

##### 응답
###### 성공
```json
{ 
  "message": "Success", 
  "data": 
   { "insu_name":insurance_company_name,
     "car_no":car_no,
     "car_name":car_name,
     "due_date":ex_policy_due_date
   }
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 비교결과(POST `result-list/` or `recall-list/`)
- result-list : 입력된 조건 기준에 대한 보험사별 보험료 비교
-  recall-list : 조건 변경시 보험사별 보험료 재 비교 

##### 요청
```bash
curl -X "POST" "${BASE_URL}result-list/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f",  # 인증번호 요청에서 수신한 `session_id`
           "manufacturer" : "현대"   # 제조사 
           ... (세부내용 별첨 참조)
}'
```

##### 응답
###### 성공
```json
{
 "message":"Success",
 "data":
  [
   {
    "expect_cost":"396,920",  # 보험료
    "applied_expect_cost":"396,920",  # 마일리지 할인 적용 보험료
    "insu_name":"캐롯손해보험",  # 보험사
    "dc_list":  # 보함사별 적용된 할인 리스트
        [
            {"dcName":"마일리지 할인"},
            {"dcName":"E-mail 할인"}
        ]
   },
   {
    "expect_cost":"399,930",
    "applied_expect_cost":"324,450",
    "insu_name":"삼성화재해상보험",
    "dc_list":
        [
            {"dcName":"블랙박스 할인"},
            {"dcName":"마일리지 할인"},
            {"dcName":"E-mail 할인"}
        ]    
   },
   ...
  ]
}
```

###### 실패(400)
다모아 진행 실패(인증번호 틀림 등)

```json
{
  "message": fail message text
}
```

###### 실패(406)
다모아 서비스 거부 대상(최근 4주내 갱신계약 완료자 등)

```json
{
  "message": "Deny Service"
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 서비스 시간 연장(POST `init-timeout/`)
- 세션 타임아웃타임을 초기값으로 리뉴얼

##### 요청
```bash
curl -X "POST" "${BASE_URL}init-timeout/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f"  # 인증번호 요청에서 수신한 `session_id`
}'
```

##### 응답
###### 성공
```json
{
  "message": "Success"
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 서비스 종료(POST `shutdown-browser/`)
- 서비스 종료, 부여받은 세션키 및 자원 반환

##### 요청
```bash
curl -X "POST" "${BASE_URL}shutdown-browser/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "session_id": "2cfe55fedbe6f1f8ecb4228f7ac1317f"  # 인증번호 요청에서 수신한 `session_id`
}'
```

##### 응답
###### 성공
```json
{
  "message": "Success"
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 차종리스트(POST `get-select-carlist/`)
- 차종 구분 단계별 실시간 리스트 제공
- 해당 요청 단계에 필요하지 않은 항목도  포함하고 값은 null 또는 임의 기재
##### 요청(step1)
```bash
curl -X "POST" "${BASE_URL}get-select-carlist/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "next-col": "car_name",  # 요청하는 차량 구분 단계, car_name -> register_year -> detail_name -> detail-option 순
           "manufacturer" : "현대",  # 제조사 (현대, 기아, 삼성, 대우, 쌍용, 외산)
           "car_name" : "",  # 차명
           "register_year" : "",  # 등록년도
           "detail_name" : "",  # 세부차명
           "start_date" : "2020-01-01"  # YYYY-MM-DD,
}'
```
##### 요청(step2)
```bash
curl -X "POST" "${BASE_URL}get-select-carlist/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "next-col": "register_year",  # 요청하는 차량 구분 단계, car_name -> register_year -> detail_name -> detail-option 순
           "manufacturer" : "현대",  # 제조사 (현대, 기아, 삼성, 대우, 쌍용, 외산)
           "car_name" : "그랜져",  # 차명
           "register_year" : "",  # 등록년도
           "detail_name" : "",  # 세부차명
           "start_date" : "2020-01-01"  # YYYY-MM-DD,
}'
```
##### 응답
###### 성공
```json
{
  "message": "Success"
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail"
}
```

#### 차종검색(POST `search-carnum/`)
- 차종 구분 단계별 실시간 리스트 제공
- 해당 요청 단계에 필요하지 않은 항목도  포함하고 값은 null 또는 임의 기재

##### 요청
```bash
curl -X "POST" "${BASE_URL}search-carnum/" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
           "car_no": "12누3374"  # 차량번호 12가3456
}'
```
##### 응답

###### 성공
```json
{
    "message": "Success",
    "ip": "3.35.244.243",  # 테스트 시에만 표기됩니다.
    "data": {
        "car_name": "Nissan",
        "detail_option": "2인승 370Z(오토,ABS,AIR-D,IM)(가솔린)",
        "register_year": "2011",
        "car_code": "964C6",
        "manufacturer": "외산",
        "detail_name": "370Z"
    }
}
```

###### 실패(500)
API 서버 내 처리 실패

```json
{
  "message": "Fail", "data": "no match_list"
}
```

##별첨
비교결과 요청시 Request 항목(result\_list, recall\_list)

| 구분 | 설명 | Code | 비고 |
|---|---|---|---|
|start_date|보험개시일|YYYY-MM-DD|
|manufacturer|제조사|현대, 기아 ,삼성 ,대우 ,쌍용, 외산|
|car\_name|차명|get-select-carlist 리턴된 값 사용|
|car\_register\_year|등록년월|get-select-carlist 리턴된 값 사용|
|detail\_car\_name|세부차명|get-select-carlist 리턴된 값 사용|
|detail\_option|세부옵션|get-select-carlist 리턴된 값 사용|
|treaty\_range|운전자범위|피보험자1인, 피보험자1인+지정1인<br>누구나, 부부한정, 가족한정(형제자매 제외),<br>가족한정+형제자매|
|driver\_year|최소연령운전자<br>생년|YYYY|
|driver\_month|월|MM|
|driver\_day|일|DD|
|driver2\_year|배우자or지정1인<br>생년|YYYY|
|driver2\_month|월|MM|
|driver2\_day|일|DD|
|coverage\_bil|대인배상II|가입, 미가입|
|coverage\_pdl|대물배상|2천만원,3천만원,5천만원,<br>1억원,2억원,3억원,5억원|
|coverage\_mp\_list|자기신체손해/자동차상해 구분|미가입, 자기신체손해, 자동차상해|
|coverage\_mp|가입금액|1천5백만원/1천5백만원, 3천만원/1천5백만원,<br>5천만원/1천5백만원, 1억원/1천5백만원|자기신체손해 선택시|
|coverage\_mp|가입금액|1억원/2천만원, 1억원/3천만원,<br>2억원/2천만원, 2억원/3천만원|자동차상해 선택시|
|coverage\_umbi|무보험차상해|가입(2억원), 미가입|
|coverage\_cac|자기차량손해|가입, 미가입|
|treaty\_ers|긴급출동서비스|가입, 미가입|
|treaty\_charge|물적사고 할증기준|50만원, 100만원, 150만원 ,200만원|
|discount\_bb|블랙박스할인|NO, YES|
|discount\_bb\_year|블랙박스구입년|YYYY|
|discount\_bb\_month|블랙박스구입월|MM|
|discount\_bb\_price|블랙박스구입금액|숫자만 # 10 < 10만원|
|discount\_mileage|마일리지할인|NO, YES|
|discount\_dist|마일리지할인거리|2,000km, 3,000km<br>.. (1,000km단위) ..<br>19,000km, 20,000km|마일리지할인 YES시
|discount\_child|자녀할인|NO, YES|
|fetus|태아여부|YES|자녀할인 YES시<br>값이 NULL이 아니면 태아로 인식|
|discount\_child\_year|자녀생년|YYYY|자녀할인 YES시&<br>태아 아닐시|
|discount\_child\_month|월|MM|자녀할인 YES시&<br>태아 아닐시|
|discount\_child\_day|일|DD|자녀할인 YES시&<br>태아 아닐시|
|discount\_pubtrans|대중교통할인|NO, YES|운전자범위(treaty\_range)가<br>1인한정, 부부한정인 경우만 가능|
|discount\_pubtrans\_cost|대중교통요금|6만원 이상, 12만원 이상|1인한정시|
|discount\_pubtrans\_cost|대중교통요금|12만원 이상, 24만원 이상|부부한정시|
|discount\_safedriving|안전운전할인(Tmap)|NO, YES|
|discount\_safedriving\_score|안전운전할인(Tmap)점수|61  # string(2)|61점 이상시 할인 반영
|discount\_safedriving\_h|안전운전할인(현대)|NO, YES|
|discount\_safedriving\_score\_h|안전운전할인(현대)점수|61  # string(2)|61점 이상시 할인 반영
|discount\_email|E-MAIL할인|NO, YES|
|discount\_poverty|서민할인|NO, YES|
|discount\_premileage|과거주행거리할인|NO, YES|미사용 추천
|discount\_premileage\_average|과거연평균주행거리|10000  # string(5)|과거주행거리할인 YES시|
|discount\_premileage\_immediate|직전연평균주행거리|10000  # string(5)| 과거주행거리할인 YES시|
|discount\_and|사고통보장치할인|NO, YES|
|discount\_adas|차선이탈방지장치할인|NO, YES|
|discount\_fca|전방충돌방지장치할인|NO, YES|
