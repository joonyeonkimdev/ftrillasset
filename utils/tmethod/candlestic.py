# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:46:51 2023

@author: 박지호
"""
import pandas as pd
from datetime import datetime
from datetime import timedelta
import Analyzer
from mpl_finance import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def candlestic(company_name,start_date=None, end_date=None):
    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    start_date = "2022-01-12"
    end_date = "2023-01-12"
    df= mk.get_daily_price(company_name, start_date, end_date)#타입에러
    df.info()
    print(df)




    df['number'] = df.index.map(mdates.date2num)
    ohlc = df[['number','OPEN','HIGH','LOW','CLOSE']]

    ndays_HIGH = df.HIGH.rolling(window=14, min_periods=1).max()            
    ndays_LOW = df.LOW.rolling(window=14, min_periods=1).min()              
    fast_k = (df.CLOSE - ndays_LOW) / (ndays_HIGH - ndays_LOW) * 100        
    slow_d = fast_k.rolling(window=3).mean()                                
    df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()                   



    plt.figure(figsize=(9,9))
    p1 = plt.subplot(3,1,1)
    plt.title('momentum')
    plt.grid(True)
    candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')
    p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    #plt.plot(df.number, df['ema130'], color='c', label='ema130')
    plt.show()
    plt.savefig('momentum.png')
    return 'momentum.png'
