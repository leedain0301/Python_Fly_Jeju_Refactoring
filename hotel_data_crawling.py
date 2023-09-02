from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import re
from glob import glob
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from tqdm import tqdm

# 크롬창 뜨지않도록.
options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome('/content/drive/MyDrive/chromedriver_win32', options=options)

# 크롤링 코드
def crawling_code(num):
    crawling = []
    for page_num in tqdm(range(num)):

        url = f'https://hotels.naver.com/list?placeFileName=place%3AJeju_Province&adultCnt=1&includeTax=false&sortField=popularityKR&sortDirection=descending&pageIndex={page_num}'
        driver.get(url)
        time.sleep(1)

        hotel_info = driver.find_element(By.CSS_SELECTOR, 'ul.SearchList_SearchList__CtPf8')
        li_tags = hotel_info.find_elements(By.TAG_NAME, 'li')
        for i in li_tags:
            # try:
            # 호텔명
            hotel_name = i.find_element(By.CSS_SELECTOR, 'h4').text

            # 호텔 주소(ex. 서귀포, 대한민국 -> split사용해서 서귀포만 저장)
            temp_hotel_address = i.find_element(By.CSS_SELECTOR, 'i.Detail_location__u3_N6').text
            hotel_address = temp_hotel_address.split(',')[0]

            try:
                # 호텔 별점
                hotel_rating = i.find_element(By.CSS_SELECTOR, 'i.Detail_score__UxnqZ').text
                if hotel_rating == '평점없음':
                    hotel_rating = 0
                else:
                    hotel_rating = float(hotel_rating)
            except :
                hotel_rating = 0

            try:
                # 호텔 성급 (ex. 5성급 -> 5 만 저장)
                temp_hotel_star = i.find_element(By.CSS_SELECTOR, 'i.Detail_grade__y5BmJ').text
                hotel_star = int(re.sub('[^0-9]', '', temp_hotel_star))
            except :
                hotel_star = 0
            
            try:
                # 호텔 가격 (ex. 296,000원~ -> 296000 만 저장.)
                temp_hotel_price = i.find_element(By.CSS_SELECTOR, 'em.Price_show_price__iQpms').text
                if temp_hotel_price:
                    hotel_price = int(re.sub('[^0-9]', '', temp_hotel_price))
                else:
                    hotel_price = 0
            except :
                hotel_price = 0
            
            time.sleep(1)
            hotel_data = {'hotel_name': hotel_name, 
                        'hotel_address': hotel_address, 
                        'hotel_rating': hotel_rating,
                        'hotel_star': hotel_star, 
                        'hotel_price': hotel_price}
            crawling.append(hotel_data)


    return crawling

dict_crawling_data = crawling_code(2)
frame_crawling_data = pd.DataFrame(dict_crawling_data)
driver.quit()


# 서비스 계정 키 JSON 파일 경로
key_path = glob('app/config/*.json')[1]


# Credentials 객체 생성
credentials = service_account.Credentials.from_service_account_file(key_path)

# GCP 클라이언트 객체 생성
client = bigquery.Client(credentials = credentials, 
                        project = credentials.project_id)

# 데이터셋과 테이블 정보 설정
dataset_id = 'jeongsu_test'
table_id = 'hotel_crawling_data'

# BigQuery 테이블에 데이터 적재
table_ref = client.dataset(dataset_id).table(table_id)
job_config = bigquery.LoadJobConfig()
job_config.write_disposition = bigquery.WriteDisposition.WRITE_APPEND 
job_config.autodetect = True  # 스키마 자동 감지 설정
job = client.load_table_from_dataframe(frame_crawling_data, table_ref, job_config=job_config)
job.result()  # 작업 완료 대기

print("데이터가 성공적으로 BigQuery에 적재되었습니다.")