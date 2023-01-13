# -*- coding: utf-8 -*-
"""
Created on Thu Jan 12 16:46:51 2023

@author: 박지호
"""
from pathlib import Path
import pandas as pd
from datetime import datetime
from datetime import timedelta
import utils.stockdb.Analyzer as Analyzer
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def candlestic(company_name,start_date=None, end_date=None):
    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df= mk.get_daily_price(company_name, start_date, end_date)#타입에러

    df['number'] = df.index.map(mdates.date2num)
    ohlc = df[['number','OPEN','HIGH','LOW','CLOSE']]

    ndays_HIGH = df.HIGH.rolling(window=14, min_periods=1).max()            
    ndays_LOW = df.LOW.rolling(window=14, min_periods=1).min()              
    fast_k = (df.CLOSE - ndays_LOW) / (ndays_HIGH - ndays_LOW) * 100        
    slow_d = fast_k.rolling(window=3).mean()                                
    df = df.assign(fast_k=fast_k, slow_d=slow_d).dropna()                   

    plt.figure(figsize=(9,9))
    p1 = plt.subplot(3,1,1)
    plt.title('candlestic')
    plt.grid(True)
    candlestick_ohlc(p1, ohlc.values, width=.6, colorup='red', colordown='blue')
    p1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    timestamp =  datetime.now().timestamp()
    filename = 'candlestic' + str(timestamp) + '.png'
    plt.savefig('/static/images/' + filename)
    print('/static/images/' + filename)
    return filename
