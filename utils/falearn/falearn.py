# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 16:02:03 2023

@author: user
"""

def predict(code):
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import warnings
    import os



    plt.rcParams['font.family'] = 'NanumGothic'

    import Analyzer

    mk = Analyzer.MarketDB()
    stock = mk.get_daily_price(code,'2018-05-04')
    #,'2018-05-04','2020-01-22'


    from sklearn.preprocessing import MinMaxScaler

    scaler = MinMaxScaler()

    scale_cols = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    scaled = scaler.fit_transform(stock[scale_cols])
    scaled

    df = pd.DataFrame(scaled, columns=scale_cols)

    from sklearn.model_selection import train_test_split

    x_train, x_test, y_train, y_test = train_test_split(df.drop('CLOSE', 1), df['CLOSE'], test_size=0.2, random_state=0, shuffle=False)

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



    WINDOW_SIZE=20
    BATCH_SIZE=30


    train_data = windowed_dataset(y_train, WINDOW_SIZE, BATCH_SIZE, True)
    test_data = windowed_dataset(y_test, WINDOW_SIZE, BATCH_SIZE, False)


    for data in train_data.take(1):
        print(f'데이터셋(X) 구성(batch_size, window_size, feature갯수): {data[0].shape}')
        print(f'데이터셋(Y) 구성(batch_size, window_size, feature갯수): {data[1].shape}')

    ## 모델

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


    earlystopping = EarlyStopping(monitor='val_loss', patience=10)

    filename = os.path.join('tmp', 'ckeckpointer.ckpt')
    checkpoint = ModelCheckpoint(filename, 
                                 save_weights_only=True, 
                                 save_best_only=True, 
                                 monitor='val_loss', 
                                 verbose=1)

    history = model.fit(train_data, 
                        validation_data=(test_data), 
                        epochs=30, 
                        callbacks=[checkpoint, earlystopping])

    model.load_weights(filename)
    pred = model.predict(test_data)
    plt.figure(figsize=(12, 9))
    plt.plot(np.asarray(y_test)[10:], label='actual')
    plt.plot(pred, label='prediction')
    plt.legend()
    plt.show()
    pred.shape
    y_test.shape
    y_test
    pred
    price = stock.CLOSE[-1] * pred[-1] / df.iloc[-1,3]
    #print("내일 주가 :", stock.CLOSE[-1] * pred[-1] / df.iloc[-1,3], 'KRW')
    return price
    