# -*- coding: utf-8 -*-
import pandas as pd
import pymysql
from datetime import datetime
from datetime import timedelta
import re
import utils.loading.confidential as confidential

class MarketDB:
    def __init__(self):
        """ 생성자: Mariadb 연결 및 종목코드 dict 생성 """
        self.conn = pymysql.connect\
            (host="localhost", port=3306, db="FTRILL", user="root", password=confidential.get_confidential('databasepw.json', "PASSWORD"), charset="utf8")
        self.codes = {}
        self.get_comp_info()
    
    def __del__(self):
        """ 소멸자: Mariadb 연결 해제 """
        self.conn.close()
        
    def get_comp_info(self):
        """ DB에서 종목코드 SELECT 후 codes에 저장 """
        sql = "SELECT * FROM COMPANY_INFO_TB"
        krx = pd.read_sql(sql, self.conn)
        for idx in range(len(krx)):
            self.codes[krx["CODE"].values[idx]] = krx["COMPANY"].values[idx]
        
    def get_daily_price(self, code, start_date=None, end_date=None):
        """ 
            특정 종목 시세를 데이터프레임 형태로 반환
                - code       : KRX종목코드 또는 상장기업명
                - start_date : 조회 시작일. 미입력 시 1년전 오늘.
                - end_date   : 조회 종료일. 미입력 시 오늘.
        """
        # 조회 시작일 초기화 및 정규화 처리
        if start_date is None:
            one_year_ago = datetime.today() - timedelta(days=365)
            start_date = one_year_ago.strftime("%Y-%m-%d")
            print("start_date is initialized to {}".format(start_date))
        else:
            start_lst = re.split("\D+", start_date)
            if (start_lst[0] == ''):
                start_lst = start_lst[1:]
            start_year = int(start_lst[0])
            start_month = int(start_lst[1])
            start_day = int(start_lst[2])
            if start_year < 1900 or start_year > int(datetime.today().strftime("%Y")):
                print(f"ValueError: start_year({start_year:d}) is out-of-range")
                return
            if start_month < 1 or start_month > 12:
                print(f"ValueError: start_month({start_month:d}) is out-of-range")
                return
            if start_day < 1 or start_day > 31:
                print(f"ValueError: start_day({start_day:d}) is out-of-range")
                return
            start_date = f"{start_year:04d}-{start_month:02d}-{start_day:02d}"
            
        # 조회 종료일 초기화 및 정규화 처리
        if end_date is None:
            end_date = datetime.today().strftime("%Y-%m-%d")
            print("end_date is initialized to {}".format(end_date))
        else:
            end_lst = re.split("\D+", end_date)
            if (end_lst[0] == ''):
                end_lst = end_lst[1:]
            end_year = int(end_lst[0])
            end_month = int(end_lst[1])
            end_day = int(end_lst[2])
            if end_year < 1900 or end_year > int(datetime.today().strftime("%Y")):
                print(f"ValueError: end_year({end_year:d}) is out-of-range")
                return
            if end_month < 1 or end_month > 12:
                print(f"ValueError: end_month({end_month:d}) is out-of-range")
                return
            if end_day < 1 or end_day > 31:
                print(f"ValueError: end_day({end_day:d}) is out-of-range")
                return
            end_day = f"{end_year:04d}-{end_month:02d}-{end_day:02d}"
        
        # 종목코드/종목명 검색 알고리즘
        codes_keys = list(self.codes.keys())
        codes_values = list(self.codes.values())  
        if code in codes_keys: #code가 종목코드일 시
            pass
        elif code in codes_values: #code가 종목명일 시 
            idx = codes_values.index(code)
            code = codes_keys[idx]
        else:
            print("ValueError: Code({}) doesn't exist".format(code))
            return
            
        # DB SELECT
        sql = f"SELECT * FROM DAILY_PRICE_TB WHERE CODE = '{code}' AND DATE BETWEEN '{start_date}' AND '{end_date}'"
        df = pd.read_sql(sql, self.conn)
        df.index = df["DATE"]
        return df
    
    
        