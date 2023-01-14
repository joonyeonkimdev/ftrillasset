# -*- coding: utf-8 -*-
"""
Created on Sat Jan  7 15:39:15 2023

@author: 박지호
"""

import pandas as pd
import pymysql
import utils.stockdb.Analyzer as Analyzer



def mmt():
         



         mk = Analyzer.MarketDB()
         start_date = "2022-01-12"
         end_date = "2023-01-12"
         stock_count = 600
         connection = pymysql.connect(host='localhost', port=3306, 
            db='FTRILL', user='root', passwd='1234', charset="utf8")
         cursor = connection.cursor()
        
        # 사용자가 입력한 시작일자를 DB에서 조회되는 일자로 보정 
         sql = f"select max(date) from daily_price_tb where date <= '{start_date}'"
         cursor.execute(sql)
         result = cursor.fetchone()
         if (result[0] is None):
            print ("start_date : {} -> returned None".format(sql))
       


        # 사용자가 입력한 종료일자를 DB에서 조회되는 일자로 보정
         sql = f"select max(date) from daily_price_tb where date <= '{end_date}'"
         cursor.execute(sql)
         result = cursor.fetchone()
         if (result[0] is None):
            print ("end_date : {} -> returned None".format(sql))
      


        # KRX 종목별 수익률을 구해서 2차원 리스트 형태로 추가
         rows = []
         columns = ['code', 'company', 'old_price', 'new_price', 'returns']
         for _, code in enumerate(mk.codes):            
            sql = f"select close from daily_price_tb "\
                f"where code='{code}' and date='{start_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            old_price = int(result[0])
            sql = f"select close from daily_price_tb "\
                f"where code='{code}' and date='{end_date}'"
            cursor.execute(sql)
            result = cursor.fetchone()
            if (result is None):
                continue
            new_price = int(result[0])
            returns = (new_price / old_price - 1) * 100
            rows.append([code, mk.codes[code], old_price, new_price, 
                returns])

         f = pd.read_csv("DGS1.csv")
         idx = f[f['DGS1'] == "."].index
         f.drop(idx , inplace=True)
         f = f.astype({'DGS1':'float'})
         a = (f['DGS1'].mean())   

        
        # 상대 모멘텀 데이터프레임을 생성한 후 수익률순으로 출력, 절대모멘텀 수익률 출력
         df = pd.DataFrame(rows, columns=columns)
         df = df[['code', 'company', 'old_price', 'new_price', 'returns']]
         df = df.sort_values(by='returns', ascending=False)
         df = df.head(stock_count)
         df.index = pd.Index(range(stock_count))
         connection.close()
         aaa= df[df['returns'] > a ]
         print(aaa)
         print(f"\nAbasolute momentum ({start_date} ~ {end_date}) : "\
            f"{df['returns'].mean():.2f}%")
         return list(aaa['code'])
         
    




