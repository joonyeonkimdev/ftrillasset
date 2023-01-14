# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 15:21:50 2023

@author: PC
"""

import pandas as pd
import matplotlib.pyplot as plt
import datetime
from datetime import timedelta
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import utils.stockdb.Analyzer as Analyzer

def tsgraph(company_name,start_date=None,end_date=None):
    
    
    plt.rc("font",family="Malgun Gothic")

    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df= mk.get_daily_price(company_name,start_date=None,end_date=None)


    ema60=df.CLOSE.ewm(span=60).mean()           # 1. 종가의 12주 지수 이동평균
    ema130=df.CLOSE.ewm(span=130).mean()         # 2. 종가의 26주 지수 이동평균
    macd=ema60 - ema130                          # 3. MACD 선
    signal=macd.ewm(span=45).mean()              # 4. 신호선(MACD의 9주 지수 이동평균)
    macdhist=macd-signal                         # 5. MACD 히스토그램

    
#1. 종가의 12주 지수 이동평균에 해당하는 60일 지수 이동평균을 구한다.
#2. 종가의 26주 지수 이동평균에 해당하는 130일 지수 이동평균을 구한다.
#3. 12주(60일) 지수 이동평균에서 26주(130일) 지수 이동평균을 빼서 MACD선을 구한다.
#4. MACD의 9주(45일) 지수 이동평균을 구해서 신호선으로 저장한다.
#5. MACD 선에서 신호선을 빼서 MACD 히스토그램을 구한다.
#6. 캔들차트에 사용할 수 있게 날짜(date)형 인덱스를 숫자형으로 변환한다.
#7. ohlc의 숫자형 일자, 시가, 저가, 종가 값을 이용해서 캔들차트를 그린다.


    df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()

    df['number'] = df.index.map(mdates.date2num)
    ohlc = df[['number','OPEN','HIGH','LOW','CLOSE']]

    ndays_HIGH = df.HIGH.rolling(window=14, min_periods=1).max()            # 1.
    ndays_LOW = df.LOW.rolling(window=14, min_periods=1).min()              # 2.
    fast_k = (df.CLOSE - ndays_LOW) / (ndays_HIGH - ndays_LOW) * 100        # 3.
    slow_d = fast_k.rolling(window=3).mean()                                # 4.
    df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()
    
#1. 14일 동안의 최댓값을 구한다. min_periods=1을 지정할 경우, 14일 기간에 해당하는 
#   데이터가 모두 누락되지 않았더라도 최소 기간인 1일 이상의 데이터만 존재하면 최댓값을 
#   구하라는 의미이다.
#2. 14일 동안의 최솟값을 구한다. min_periods=1로 지정하면, 14일 치 데이터 모두 누락
#   되지 않았더라도 최소 기간인 1일 이상의 데이터만 존재하면 최솟값을 구하라는 의미이다.
#3. 빠른선 %K를 구한다.
#4. 3일 동안 %K의 평균을 구해서 느린선 %D에 저장한다.
#5. %K와 %D로 데이터 프레임을 생성한 뒤 결측치는 제거한다.
#6. Y축 눈금을 0,20,80,100으로 설정하여 스토캐스틱의 기준선을 나타낸다.

    plt.figure(figsize=(9,9))
    p1 = plt.subplot(3,1,1)
    plt.title('삼중창 그래프')
    plt.grid(True)
    candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')
    p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.plot(df.number, df['ema130'], color='c', label='130일 지수이동 평균')
    for i in range(1, len(df.CLOSE)):
        if df.ema130.values[i-1] < df.ema130.values[i] and \
            df.slow_d.values[i-1] >= 20 and df.slow_d.values[i] < 20:   # 1. 
            plt.plot(df.number.values[i], 250000, 'r^')                 # 2.
        elif df.ema130.values[i-1] > df.ema130.values[i] and \
            df.slow_d.values[i-1] <= 80 and df.slow_d.values[i] > 80 :  # 3.
            plt.plot(df.number.values[i], 250000,'bv')                 # 4.
            plt.legend(loc='best')


    
#1. 130일 이동 지수 평균이 상승하고 %D가 20 아래로 떨어지면 #2. 빨간색 삼각형으로 매수
#   신호 (▲) 를 표시한다.
#3. 130일 이동 지수 평균이 하락하고 %D가 80 위로 상승하면 #4. 파란색 삼각형으로 매수
#    신호 (▼) 를 표시한다.



    p2 = plt.subplot(3,1,2)
    plt.grid(True)
    p2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.bar(df.number, df['macdhist'], color='m', label='MACD 히스토그램')
    plt.plot(df.number, df['macd'], color='b', label='MACD')
    plt.plot(df.number, df['signal'], 'g--', label='신호선')
    plt.legend(loc='best')

    p3 = plt.subplot(3,1,3)
    plt.grid(True)
    p3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.plot(df.number, df['fast_k'], color='c', label='%K')
    plt.plot(df.number, df['slow_d'], color='k', label='%D')
    plt.yticks([0,20,80,100])
    plt.legend(loc='best')
    plt.show()
    
    plt.savefig('Triplescreen.png')
    return

def tsrevenue(company_name,start_date=None,end_date=None):

#수익률

    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df= mk.get_daily_price(company_name,start_date=None,end_date=None)

    
    ema60=df.CLOSE.ewm(span=60).mean()           # 1. 종가의 12주 지수 이동평균
    ema130=df.CLOSE.ewm(span=130).mean()         # 2. 종가의 26주 지수 이동평균
    macd=ema60 - ema130                          # 3. MACD 선
    signal=macd.ewm(span=45).mean()              # 4. 신호선(MACD의 9주 지수 이동평균)
    macdhist=macd-signal  

    df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()
    df['number'] = df.index.map(mdates.date2num)
    ohlc = df[['number','OPEN','HIGH','LOW','CLOSE']]

    ndays_HIGH = df.HIGH.rolling(window=14, min_periods=1).max()            # 1.
    ndays_LOW = df.LOW.rolling(window=14, min_periods=1).min()              # 2.
    fast_k = (df.CLOSE - ndays_LOW) / (ndays_HIGH - ndays_LOW) * 100        # 3.
    slow_d = fast_k.rolling(window=3).mean()                                # 4.
    df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()  
    
    buy_Price=0     
    sell_Price=0
    gross_rr = 1

    for i in range(1, len(df.CLOSE)) :
        if df.ema130.values[i-1] < df.ema130.values[i] and  df.slow_d.values[i-1] >= 20 and df.slow_d.values[i] < 20:  
                print(df.CLOSE.values[i])
                if buy_Price==0:
                    buy_Price=df.CLOSE.values[i]
                
                else:
                    continue
        if df.ema130.values[i-1] > df.ema130.values[i] and df.slow_d.values[i-1] <= 80 and df.slow_d.values[i] > 80:
                print(df.CLOSE.values[i])
                if buy_Price>0 and sell_Price==0:
                    sell_Price=df.CLOSE.values[i]
                    
                else:
                    continue
    if buy_Price > 0 and sell_Price > 0:
        rr=(sell_Price-buy_Price)/buy_Price
        gross_rr *= rr
    
    return gross_rr


def signal(company_name,start_date=None,end_date=None):
    

        Analyzer.MarketDB()
        mk = Analyzer.MarketDB()
        df= mk.get_daily_price(company_name,start_date=None,end_date=None)

        
        ema60=df.CLOSE.ewm(span=60).mean()           # 1. 종가의 12주 지수 이동평균
        ema130=df.CLOSE.ewm(span=130).mean()         # 2. 종가의 26주 지수 이동평균
        macd=ema60 - ema130                          # 3. MACD 선
        signal=macd.ewm(span=45).mean()              # 4. 신호선(MACD의 9주 지수 이동평균)
        macdhist=macd-signal  

        df = df.assign(ema130=ema130, ema60=ema60, macd=macd, signal=signal, macdhist=macdhist).dropna()
        df['number'] = df.index.map(mdates.date2num)
        ohlc = df[['number','OPEN','HIGH','LOW','CLOSE']]

        ndays_HIGH = df.HIGH.rolling(window=14, min_periods=1).max()            # 1.
        ndays_LOW = df.LOW.rolling(window=14, min_periods=1).min()              # 2.
        fast_k = (df.CLOSE - ndays_LOW) / (ndays_HIGH - ndays_LOW) * 100        # 3.
        slow_d = fast_k.rolling(window=3).mean()                                # 4.
        df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()  
        
        buy_Price=0     
        sell_Price=0
        
        
        for i in range(1, len(df.CLOSE)) :
            if df.ema130.values[i-1] < df.ema130.values[i] and  df.slow_d.values[i-1] >= 20 and df.slow_d.values[i] < 20:  
                print('1', df.DATE.values[i],df.CLOSE.values[i])
            if df.ema130.values[i-1] > df.ema130.values[i] and df.slow_d.values[i-1] <= 80 and df.slow_d.values[i] > 80:
                print('2', df.DATE.values[i],df.CLOSE.values[i])
        
            
        dic = {1:df.CLOSE.values[i],2:df.CLOSE.values[i]}
        
   
    
        