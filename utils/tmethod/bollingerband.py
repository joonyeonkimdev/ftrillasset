# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 15:07:34 2023

@author: mimm
"""
from pathlib import Path
import matplotlib.pyplot as plt
import sys
import pandas as pd
import utils.stockdb.Analyzer as Analyzer
import datetime
from datetime import timedelta
from matplotlib import font_manager, rc

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def bollingerband1(company_name, start_date=None, end_date=None):
    plt.rc("font",family="Malgun Gothic")

    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df = mk.get_daily_price(
        company_name, start_date=None, end_date=None)  # 타입에러
    df['MA20'] = df['CLOSE'].rolling(window=20).mean()
    df['STUDDEV'] = df['CLOSE'].rolling(window=20).std()
    df['UPPER'] = df['MA20']+(df['STUDDEV']*2)
    df['LOWER'] = df['MA20']-(df['STUDDEV']*2)
    df['PB'] = (df['CLOSE']-df['LOWER'])/(df['UPPER']-df['LOWER'])  # %b
    df['TP'] = (df['HIGH']+df['LOW']+df['CLOSE'])/3
    df['PMF'] = 0
    df['NMF'] = 0
    # 현금지표
    for i in range(len(df.CLOSE)-1):
        if df.TP.values[i] < df.TP.values[i+1]:
            df.PMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.NMF.values[i+1] = 0
        else:
            df.NMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.PMF.values[i+1] = 0
    # 추세매매
    df['MFR'] = df.PMF.rolling(window=10).sum()/df.NMF.rolling(window=10).sum()
    df['MFI10'] = 100-100/(1+df['MFR'])
    df[19:]

    # 밴드폭 시각화
    plt.figure(figsize=(10, 9))
    plt.subplot(2, 1, 1)
    plt.plot(df.index, df['CLOSE'], color='#0000ff', label='종가')
    plt.plot(df.index, df['UPPER'], 'r--', label='상단밴드')
    plt.plot(df.index, df['MA20'], 'k--', label='20일 이동평균')
    plt.plot(df.index, df['LOWER'], 'c--', label='하단밴드')
    plt.fill_between(df.index, df['UPPER'], df['LOWER'], color='0.9')

    # 차트시각화
    for i in range(len(df.CLOSE)):
        if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:  # 추세추종 매수
            plt.plot(df.index.values[i], df.CLOSE.values[i], 'r^')
            df[19:]
        elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:  # 추세추종 매도
            plt.plot(df.index.values[i], df.CLOSE.values[i], 'bv')
            df[19:]

    plt.legend(loc='best')
    plt.title('볼린저밴드(추세추종)')

    timestamp = datetime.datetime.now().timestamp()
    filename = 'Bollingerband1' + str(timestamp) + '.png'
    plt.savefig(str(BASE_DIR) + '/static/stock_img/' + filename, bbox_inches='tight', pad_inches=0.1)
    return filename


def bollingerband2(company_name, start_date=None, end_date=None):
    plt.rc("font",family="Malgun Gothic")

    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    dr = mk.get_daily_price(
        company_name, start_date=None, end_date=None)  # 타입에러
    dr['MA20'] = dr['CLOSE'].rolling(window=20).mean()
    dr['STUDDEV'] = dr['CLOSE'].rolling(window=20).std()
    dr['UPPER'] = dr['MA20']+(dr['STUDDEV']*2)
    dr['LOWER'] = dr['MA20']-(dr['STUDDEV']*2)
    dr['PB'] = (dr['CLOSE']-dr['LOWER'])/(dr['UPPER']-dr['LOWER'])  # %b
    dr['II'] = (2*dr['CLOSE']-dr['HIGH']-dr['LOW']) / \
        (dr['HIGH']-dr['LOW'])*dr['VOLUME']
    dr['IIP21'] = dr['II'].rolling(window=21).sum(
    )/dr['VOLUME'].rolling(window=21).sum()*100
    dr = dr.dropna()

    plt.figure(figsize=(10, 9))
    plt.subplot(2, 1, 1)
    plt.title('Bollunger band')
    plt.plot(dr.index, dr['CLOSE'], color='#0000ff', label='종가')
    plt.plot(dr.index, dr['UPPER'], 'r--', label='상단밴드')
    plt.plot(dr.index, dr['MA20'], 'k--', label='20일 이동평균')
    plt.plot(dr.index, dr['LOWER'], 'c--', label='하단밴드')
    plt.fill_between(dr.index, dr['UPPER'], dr['LOWER'], color='0.9')
    for i in range(0, len(dr.CLOSE)):
        if dr.PB.values[i] < 0.05 and dr.IIP21.values[i] > 0:
            plt.plot(dr.index.values[i], dr.CLOSE.values[i], 'r^')
        elif dr.PB.values[i] > 0.95 and dr.IIP21.values[i] < 0:
            plt.plot(dr.index.values[i], dr.CLOSE.values[i], 'bv')

    plt.legend(loc='best')
    plt.title('볼린저밴드(반전매매)')

    timestamp = datetime.datetime.now().timestamp()
    filename = 'Bollingerband2' + str(timestamp) + '.png'
    plt.savefig(str(BASE_DIR) + '/static/stock_img/' + filename, bbox_inches='tight', pad_inches=0.1)
    return filename


def earingrate(company_name, start_date=None, end_date=None):
    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df = mk.get_daily_price(
        company_name, start_date, end_date)
    dr = mk.get_daily_price(
        company_name, start_date, end_date)
    # 수익률
    df['MA20'] = df['CLOSE'].rolling(window=20).mean()
    df['STUDDEV'] = df['CLOSE'].rolling(window=20).std()
    df['UPPER'] = df['MA20']+(df['STUDDEV']*2)
    df['LOWER'] = df['MA20']-(df['STUDDEV']*2)
    df['PB'] = (df['CLOSE']-df['LOWER'])/(df['UPPER']-df['LOWER'])  # %b
    df['TP'] = (df['HIGH']+df['LOW']+df['CLOSE'])/3
    df['PMF'] = 0
    df['NMF'] = 0
    # 현금지표
    for i in range(len(df.CLOSE)-1):
        if df.TP.values[i] < df.TP.values[i+1]:
            df.PMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.NMF.values[i+1] = 0
        else:
            df.NMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.PMF.values[i+1] = 0
            df.NMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.PMF.values[i+1] = 0
           # 추세매매
    df['MFR'] = df.PMF.rolling(window=10).sum()/df.NMF.rolling(window=10).sum()
    df['MFI10'] = 100-100/(1+df['MFR'])
    # 반전매매
    dr['MA20'] = dr['CLOSE'].rolling(window=20).mean()
    dr['STUDDEV'] = dr['CLOSE'].rolling(window=20).std()
    dr['UPPER'] = dr['MA20']+(dr['STUDDEV']*2)
    dr['LOWER'] = dr['MA20']-(dr['STUDDEV']*2)
    dr['PB'] = (dr['CLOSE']-dr['LOWER'])/(dr['UPPER']-dr['LOWER'])  # %b
    dr['II'] = (2*dr['CLOSE']-dr['HIGH']-dr['LOW']) / \
        (dr['HIGH']-dr['LOW'])*dr['VOLUME']
    dr['IIP21'] = dr['II'].rolling(window=21).sum()/dr['VOLUME'].rolling(window=21).sum()*100
    # 밴드폭 시각화

    buy_price = 0  # 매수
    sell_price = 0  # 매도
    gross_rr = 1  # 누적곱

    # 수익율
    for i in range(len(df.CLOSE)):
      if df.PB.values[i]>0.8 and df.MFI10.values[i]>80:     
         if buy_price==0:
            buy_price=df.CLOSE.values[i]
            print("1:",buy_price)
         else:
              continue
      elif df.PB.values[i]<0.2 and df.MFI10.values[i]<20:
          if buy_price>0 & sell_price==0:
             sell_price=df.CLOSE.values[i]
             print("2:",sell_price)
          else:
              continue
      if buy_price > 0 and sell_price > 0:
         rr=(sell_price-buy_price)/buy_price
         if rr !=0:
             gross_rr *= rr
             print("(",gross_rr)
             buy_price=0
             sell_price=0
         if rr==0:
             buy_price=0
             sell_price=0
      
    buy_price1 = 0   #매수
    sell_price1 = 0  #매도
    gross_bb = 1
     #수익율
 
    for i in range(0,len(dr.CLOSE)):
       if dr.PB.values[i]<0.05 and dr.IIP21.values[i]>0:
           if buy_price1==0:
               buy_price1=dr.CLOSE.values[i]
               print("3:",buy_price1)
           else:
                continue
       elif dr.PB.values[i]>0.95 and dr.IIP21.values[i]<0:
            if buy_price1>0 & sell_price1==0:
               sell_price1=dr.CLOSE.values[i]
               print("4:",sell_price1)
            else:
                continue
            if buy_price1 > 0 and sell_price1 > 0:
               bb=(sell_price1-buy_price1)/buy_price1
               if bb !=0:
                  gross_bb *= bb
                  print("^",gross_bb)
                  buy_price1=0
                  sell_price1=0
            if bb==0:
                buy_price1=0
                sell_pric1e=0
                    
    return round((gross_rr*gross_bb)*100, 2)

def signallist(company_name, start_date=None, end_date=None):
    Analyzer.MarketDB()
    mk = Analyzer.MarketDB()
    df = mk.get_daily_price(
        company_name, start_date=None, end_date=None)
    dr = mk.get_daily_price(
        company_name, start_date=None, end_date=None)

    df['MA20'] = df['CLOSE'].rolling(window=20).mean()
    df['STUDDEV'] = df['CLOSE'].rolling(window=20).std()
    df['UPPER'] = df['MA20']+(df['STUDDEV']*2)
    df['LOWER'] = df['MA20']-(df['STUDDEV']*2)
    df['PB'] = (df['CLOSE']-df['LOWER'])/(df['UPPER']-df['LOWER'])  # %b
    df['TP'] = (df['HIGH']+df['LOW']+df['CLOSE'])/3
    df['PMF'] = 0
    df['NMF'] = 0
    for i in range(len(df.CLOSE)-1):
        if df.TP.values[i] < df.TP.values[i+1]:
            df.PMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.NMF.values[i+1] = 0
        else:
            df.NMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.PMF.values[i+1] = 0
            df.NMF.values[i+1] = df.TP.values[i+1]*df.VOLUME.values[i+1]
            df.PMF.values[i+1] = 0
            # 추세매매
    df['MFR'] = df.PMF.rolling(window=10).sum()/df.NMF.rolling(window=10).sum()
    df['MFI10'] = 100-100/(1+df['MFR'])

    dr['MA20'] = dr['CLOSE'].rolling(window=20).mean()
    dr['STUDDEV'] = dr['CLOSE'].rolling(window=20).std()
    dr['UPPER'] = dr['MA20']+(dr['STUDDEV']*2)
    dr['LOWER'] = dr['MA20']-(dr['STUDDEV']*2)
    dr['PB'] = (dr['CLOSE']-dr['LOWER'])/(dr['UPPER']-dr['LOWER'])  # %b
    dr['II'] = (2*dr['CLOSE']-dr['HIGH']-dr['LOW']) / \
        (dr['HIGH']-dr['LOW'])*dr['VOLUME']
    dr['IIP21'] = dr['II'].rolling(window=21).sum(
    )/dr['VOLUME'].rolling(window=21).sum()*100

    buy_price = 0  # 매수
    sell_price = 0  # 매도
    gross_rr = 1  # 누적곱
    for i in range(len(df.CLOSE)):
        if df.PB.values[i] > 0.8 and df.MFI10.values[i] > 80:
            print("1", df.DATE.values[i], df.CLOSE.values[i])
        elif df.PB.values[i] < 0.2 and df.MFI10.values[i] < 20:
            print("2", df.DATE.values[i], df.CLOSE.values[i])

    buy_price1 = 0  # 매수
    sell_price1 = 0  # 매도
    gross_bb = 1

    for i in range(0, len(dr.CLOSE)):
        if dr.PB.values[i] < 0.05 and dr.IIP21.values[i] > 0:
            print("3", dr.DATE.values[i], df.CLOSE.values[i])
        elif dr.PB.values[i] > 0.95 and dr.IIP21.values[i] < 0:
            print("4", dr.DATE.values[i], dr.CLOSE.values[i])

    dic = {"1": df.CLOSE.values[i], 2: df.CLOSE.values[i],
           3: dr.CLOSE.values[i], 4: dr.CLOSE.values[i]}
