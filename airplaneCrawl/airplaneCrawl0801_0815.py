import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import datetime


# 서비스 계정 인증 정보가 담긴 JSON 파일 경로
KEY_PATH = "./app/config/*.json"


start = time.time()

def crawl(URL): # 크롤링 함수
    driver.get(URL)

    time.sleep(4) 

    for c in range(60): # 정해진 횟수 만큼 Page down을 누른다.
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    names = driver.find_elements(By.CLASS_NAME, 'name') # 공항 이름
    leave_reach_Times = driver.find_elements(By.CLASS_NAME, 'route_time__-2Z1T') # 출발 시간, 도착 시간
    seatTypes = driver.find_elements(By.CLASS_NAME, 'domestic_type__30RSq') # 좌석 타입
    charges = driver.find_elements(By.CLASS_NAME, 'domestic_num__2roTW') # 가격

    leave_reach_Times_processed = []

    for i in range(0, len(leave_reach_Times), 2): #leave_reach_Times에는 출발시간, 도착시간, 출발시간 ... 순으로 들어있기 때문에 두개씩 나눠서 다시 저장
        leave_reach_Times_processed.append([leave_reach_Times[i].text, leave_reach_Times[i+1].text])


    seatTypes_processed = []
    indexlst = []
    for k in range(0, len(seatTypes)): # 필요 없는 정보(네이버 할인 정보)를 삭제
        seatType = seatTypes[k].text
        if '네이버' in seatType:
            indexlst.append(k)
        else:
            seatTypes_processed.append(seatType)

    charges_processed = []
    for j in range(len(charges)): # 필요 없는 정보(네이버 할인 가격)를 삭제
        if j in indexlst:
            continue
        else:
            charges_processed.append(charges[j].text)

    result = []
    for name, lrtime, seat, charge in zip(names, leave_reach_Times_processed, seatTypes_processed, charges_processed):
        result.append([name.text, lrtime[0], lrtime[1], seat, charge])

    return result

def df_list_append(datas, df, airport):
    for data in datas:
        data.append(date) # 날짜 컬럼 추가
        data.append(dayConvert(date)) # 요일 컬럼 추가
        data.append(airport) # 공항 컬럼 추가
        df.loc[len(df)] = data
    return df

def dayConvert(date):
    day = datetime.date(date//10000, date%10000//100, date%100).weekday()
    dayDate = '월화수목금토일'
    return dayDate[day]


# 옵션
options = webdriver.ChromeOptions()
options.add_argument('headless') # 화면 출력 없이 작업
options.add_argument("no-sandbox")
options.add_argument('--ignore-certificate-errors') # 인증서 관련 에러 무시
options.add_argument("--ignore-ssl-errors")
options.add_argument('window-size=1920x1080') # 브라우저 윈도우 사이즈
options.add_argument("disable-gpu") # gpu 가속 사용 x

df = pd.DataFrame(columns=['name', 'leavetime', 'reachtime', 'seat', 'charge', 'date', 'day', 'airport']) # 저장 데이터프레임

# 로드
driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options) # 드라이버 위치 경로


# goURL = 'https://flight.naver.com/flights/domestic/GMP-CJU-20230601?adult=1&fareType=Y' # 빠른 테스트용


for date in range(20230801, 20230816): # 20230801~20230815
    goURL = f'https://flight.naver.com/flights/domestic/GMP-CJU-{date}?adult=1&fareType=Y'
    backURL = f'https://flight.naver.com/flights/domestic/CJU-GMP-{date}?adult=1&fareType=Y'
    goDatas = crawl(goURL)
    df = df_list_append(goDatas, df, 'GMP')
    backDatas = crawl(backURL)
    df = df_list_append(backDatas, df, 'CJU')
        
    print(date,'데이터 완료')

driver.quit() # driver 종료

# 데이터 처리

df['charge'] = df['charge'].str.replace(',', '').astype('int')
df['leavetime'] = df['leavetime'].str.replace(':', '').astype('int')
df['reachtime'] = df['reachtime'].str.replace(':', '').astype('int')
df['date'] = df['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y-%m-%d'))
df['leavehour'] = df['leavetime'].apply(lambda x : x//100)


from google.cloud import bigquery
from google.oauth2 import service_account


# Credentials 객체 생성
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
# 빅쿼리 클라이언트 객체 생성
client = bigquery.Client(credentials = credentials, project = credentials.project_id)

# 테이블 ID
table_id = "fightproject.test_db.airplanecrawl"

# 테이블 객체 생성
table = client.get_table(table_id)
# 데이터프레임을 테이블에 삽입
client.load_table_from_dataframe(df, table)

end = time.time()

print(f"{end - start:.5f} sec") # 실행 시간 출력