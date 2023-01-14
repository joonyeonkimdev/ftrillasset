# -*- coding: utf-8 -*-
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import requests, pymysql, json
from datetime import datetime
import traceback
import utils.loading.confidential as confidential

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class DBUpdater:
    def __init__(self):
        """ 생성자: DB연결 및 종목코드 dict 생성 """
        self.conn = pymysql.connect\
            (host="localhost", port=3306, db="FTRILL", user="root", password=confidential.get_confidential('databasepw.json', "PASSWORD"), charset="utf8")
        
        with self.conn.cursor() as cursor:
            sql = """
            CREATE TABLE IF NOT EXISTS COMPANY_INFO_TB(
                CODE 	     VARCHAR(20)
                ,COMPANY 	 VARCHAR(40)
                ,LAST_UPDATE DATE
                ,PRIMARY KEY (CODE)
            )
            """
            cursor.execute(sql)
            
            sql = """
            CREATE TABLE IF NOT EXISTS DAILY_PRICE_TB(
                CODE 	VARCHAR(20)
                ,DATE   DATE
                ,OPEN   BIGINT(20)
                ,HIGH   BIGINT(20)
                ,LOW 	BIGINT(20)
                ,CLOSE  BIGINT(20)
                ,DIFF   BIGINT(20)
                ,VOLUME BIGINT(20)
                ,PRIMARY KEY(CODE, DATE)
            )
            """
            cursor.execute(sql)
        self.conn.commit()
        
        self.codes = dict()
        
    def __del__(self):
        """ 소멸자: DB 연결 해제 """
        self.conn.close()
        
    def read_krx_code(self):
        """ KRX의 상장법인 목록 파일 DataFrame로 반환 """
        url = "http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"
        krx = pd.read_html(url, header=0)[0]
        krx = krx[["종목코드", "회사명"]]
        krx = krx.rename(columns={"종목코드":"code", "회사명":"company"})
        krx.code = krx.code.map('{:06d}'.format)
        return krx
        
    def update_comp_info(self):
        """ 종목코드 DB 최신화 후 dict에 저장 """
        sql = "SELECT * FROM COMPANY_INFO_TB"
        df = pd.read_sql(sql, self.conn)
        for idx in range(len(df)):
            self.codes[df["CODE"].values[idx]] = df["COMPANY"].values[idx]
            
        with self.conn.cursor() as cursor:
            sql = "SELECT MAX(LAST_UPDATE) FROM COMPANY_INFO_TB"
            cursor.execute(sql)
            rs = cursor.fetchone()
            today = datetime.today().strftime("%Y-%m-%d")
            if rs[0] == None or rs[0].strftime("%Y-%m-%d") < today:
                krx = self.read_krx_code()
                for idx in range(len(krx)):
                    code = krx.code.values[idx]
                    company = krx.company.values[idx]
                    sql = f"REPLACE INTO COMPANY_INFO_TB (CODE, COMPANY, LAST_UPDATE) VALUES ('{code}', '{company}', '{today}')"
                    cursor.execute(sql)
                    self.codes[code] = company
                    tmnow = datetime.now().strftime("%Y-%m-%d %H:%M")
                    print(f"[{tmnow}] #{idx+1:04d} REPLACE INTO COMPANY_INFO_TB (CODE, COMPANY, LAST_UPDATE) VALUES ({code}, {company}, {today})")
                self.conn.commit()
                print('')
    
    def read_naver(self, code, company, pages_to_fetch):
        """ 네이버 금융 주가 스크래핑 후 DataFrame로 반환 """
        try:
            sise_url = f"http://finance.naver.com/item/sise_day.nhn?code={code}"
            html = requests.get(sise_url, headers={'User-agent':'Mozilla/5.0'}).text
            bs = BeautifulSoup(html, "lxml")
            pgrr = bs.find('td', class_='pgRR')
            if pgrr is None:
                return None
            s = str(pgrr.a["href"]).split("=")
            lastpage = s[-1]
            df = pd.DataFrame()
            pages = min(int(lastpage), pages_to_fetch)
            for page in range(1, pages+1):
                url = "{}&page={}".format(sise_url, page)
                res = requests.get(url, headers={'User-agent':'Mozilla/5.0'})
                df = df.append(pd.read_html(res.text, header=0)[0])
                tmnow = datetime.now().strftime("%Y-%m-%d %H:%M")
                print("[{}] {} ({}) : {:04d}/{:04d} pages are downloading...".format(tmnow, company, code, page, pages), end="\r")
            df = df.rename(columns={"날짜":"date", "종가":"close", "전일비":"diff", "시가":"open", "고가":"high", "저가":"low", "거래량":"volume"})
            df["date"] = df["date"].replace('.', '-')
            df = df.dropna()
            df[["close", "diff", "open", "high", "low", "volume"]] = df[["close", "diff", "open", "high", "low", "volume"]].astype(int)
            df = df[["date", "open", "high", "low", "close", "diff", "volume"]]
        except Exception:
            print(traceback.format_exc())
            return None
        return df
    
    # DB 100개 당 1 commit 설정
    def replace_into_db(self, df, num, code, company):
       """ 주가데이터를 DB에 REPLACE """
       with self.conn.cursor() as cursor:
           for r in df.itertuples():
               sql = f"REPLACE INTO DAILY_PRICE_TB VALUES ('{code}', '{r.date}', {r.open}, {r.high}, {r.low}, {r.close}, {r.diff}, {r.volume})"
               cursor.execute(sql) 
           self.conn.commit()
           print("[{}] #{:04d} {} ({}) : {} rows > REPLACE INTO DAILY_PRICE_TB [DONE]".format(datetime.now().strftime("%Y-%m-%d %H:%M"), num+1, company, code, len(df)))
               
    def update_daily_price(self, pages_to_fetch):
        """ 주가 DB 최신화 """
        for idx, code in enumerate(self.codes):
            df = self.read_naver(code, self.codes[code], pages_to_fetch)
            if df is None:
                continue
            self.replace_into_db(df, idx, code, self.codes[code])
        
    def execute_daily(self):
        """ 배치 역할의 함수 => 하루 한번 DB 최신화 """    
        self.update_comp_info() #종목 최신화
        try:
            with open(str(BASE_DIR) + "/config.json", "r") as in_file:
                config = json.load(in_file)
                pages_to_fetch = config["pages_to_fetch"]
        except FileNotFoundError:
            with open(str(BASE_DIR) + "/config.json", "w") as out_file: #with 구문 내 스트림은 close() 안해도 됨. => with 구문 내에서만 사용
                pages_to_fetch = 100
                config = {"pages_to_fetch":1}
                json.dump(config, out_file)
        self.update_daily_price(pages_to_fetch) #주가 최신화
        print("[{}] The database is now up-to-date".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
        
# => 아래 조건식은 Django에서 당일 최초 요청신호로 하루 한번 실행되도록 수정 예정       
if __name__ == '__main__':
    dbupdater = DBUpdater()
    dbupdater.execute_daily()
    del dbupdater
    print("The DB connection terminated")


