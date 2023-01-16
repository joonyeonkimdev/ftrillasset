# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
import utils.stockdb.Analyzer as Analyzer
import pymysql
import datetime
import utils.loading.confidential as confidential

def predict(code):
    pre_df = pd.DataFrame({'CLOSE': []})
    mk = Analyzer.MarketDB()
    stock = mk.get_daily_price(code, '2018-05-04')
    len(stock.index)
    new_index = list()
    for l in range(0, len(stock.index)):
        new_index.append(l)
    stock.index = new_index

    for i in range(1, 4):
        j = i
        plt.rcParams['font.family'] = 'NanumGothic'

        #import Analyzer

        #mk = Analyzer.MarketDB()

        stock[stock.index % j == 0]

        # ,'2018-05-04','2020-01-22'
        from sklearn.preprocessing import MinMaxScaler

        scaler = MinMaxScaler()

        scale_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

        scaled = scaler.fit_transform(stock[scale_cols])
        scaled

        df = pd.DataFrame(scaled, columns=scale_cols)

        from sklearn.model_selection import train_test_split

        x_train, x_test, y_train, y_test = train_test_split(
            df.drop('CLOSE', 1), df['CLOSE'], test_size=0.2, random_state=0, shuffle=False)

        x_train.shape, y_train.shape

        x_test.shape, y_test.shape

        import tensorflow as tf

        def windowed_dataset(series, window_size, batch_size, shuffle):
            series = tf.expand_dims(series, axis=-1)
            ds = tf.data.Dataset.from_tensor_slices(series)
            ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
            ds = ds.flat_map(lambda w: w.batch(window_size + 1))
            if shuffle:
                ds = ds.shuffle(1000)
            ds = ds.map(lambda w: (w[:-1], w[-1]))
            return ds.batch(batch_size).prefetch(1)

        WINDOW_SIZE = 20
        BATCH_SIZE = 30

        train_data = windowed_dataset(y_train, WINDOW_SIZE, BATCH_SIZE, True)
        test_data = windowed_dataset(y_test, WINDOW_SIZE, BATCH_SIZE, False)

        for data in train_data.take(1):
            print(
                f'데이터셋(X) 구성(batch_size, window_size, feature갯수): {data[0].shape}')
            print(
                f'데이터셋(Y) 구성(batch_size, window_size, feature갯수): {data[1].shape}')

        # 모델

        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, LSTM, Conv1D, Lambda
        from tensorflow.keras.losses import Huber
        from tensorflow.keras.optimizers import Adam
        from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

        model = Sequential([
            Conv1D(filters=30, kernel_size=5,
                   padding="causal",
                   activation="relu",
                   input_shape=[WINDOW_SIZE, 1]),
            LSTM(16, activation='tanh'),
            Dense(16, activation="relu"),
            Dense(1),
        ])

        loss = Huber()
        optimizer = Adam(0.0005)
        model.compile(loss=Huber(), optimizer=optimizer, metrics=['mse'])

        history = model.fit(train_data,
                            validation_data=(test_data),
                            epochs=30
                            )

        pred = model.predict(test_data)


#        print("내일 주가 :", stock.CLOSE[-1] * pred[-1] / df.CLOSE.iloc[-1], 'KRW')
        print("내일 주가 :", stock.CLOSE.iloc[-1]
              * pred[-1] / df.iloc[-1, 3], 'KRW')
        print(i)
        price = np.trunc(stock.CLOSE.iloc[-1] * pred[-1] / df.iloc[-1, 3])
        price = pd.DataFrame(price)
        price.rename(columns={0: 'CLOSE'}, inplace=True)
        pre_df = pd.concat([pre_df, price], axis=0)

    conn = pymysql.connect(host="localhost", port=3306, db="FTRILL", user="root",
                           password=confidential.get_confidential('databasepw.json', "PASSWORD"), charset="utf8")

    code = mk.get_code(code)

    with conn.cursor() as cursor:
        sql = f"SELECT MAX(DATE) FROM DAILY_PRICE_TB WHERE CODE = '{code}'"
        cursor.execute(sql)
        rs = cursor.fetchone()
        last_date = rs[0]

        days = 1
        new_last_date = ""
        for r in pre_df.itertuples():
            date = last_date + datetime.timedelta(days=days)
            date = date.strftime("%Y-%m-%d")
            new_last_date = date
            sql = f"REPLACE INTO DAILY_PRICE_TB (CODE, DATE, CLOSE) VALUES ('{code}', '{date}', {r.CLOSE})"
            cursor.execute(sql)
            days += 1
        conn.commit()
    conn.close()
    return new_last_date


def delete_predicted_db(code, last_update):
    conn = pymysql.connect(host="localhost", port=3306, db="FTRILL",
                           user="root", password=confidential.get_confidential('databasepw.json', "PASSWORD"), charset="utf8")

    mk = Analyzer.MarketDB()
    code = mk.get_code(code)

    with conn.cursor() as cursor:
        sql = f"DELETE FROM DAILY_PRICE_TB WHERE CODE = '{code}' AND DATE > '{last_update}'"
        cursor.execute(sql)
        conn.commit()
    conn.close()
    return True
