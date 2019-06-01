# pfscrap 사용 예시

## 설치 및  실행준비
>#### 셸, 프롬프트에서 코드 다운로드 후 디렉토리로 이동
```shell
>>git clone https://github.com/zwolf21/pfscrap.git
>>cd pfscrap
```
>#### 필요라이브러리 설치
```shell
>>pip install -r requirements.txt
```

## 1. 펀드리스트 조회 및 출력
```shell
>>python pfscrap kofia ls
```
> 기본적으로 현재일자로부터 1주일 전에 생성된 펀드리스트를 출력
```shell
>>python pfscrap kofia ls -sd 20180501 -ed 20180510 -o xlsx
```
> 2018.5.1 ~ 5.10 사이에 생성된 펀드리스트를 xlsx 형태로 출력

```shell
>>python pfscrap kofia ls-al -sd 20180501 -ed 20180510 -o csv
```
> 오늘로부터 1달 전까지 생성된 펀드리스트 출력
***
## 2. 가격변동 추이 조회 및 출력
#### 1 에서 구한 파일, 특정 표준코드를 사용

## 3. 결산 및 상환정보 조회 및 출력
표준 코드를 컬럼으로 갖고 있는 FundList_20180501~20180510.xlsx 파일을 이용하여 각 해당코드의 결산 및 상환 정보를 csv로 출력
