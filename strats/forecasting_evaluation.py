# -*- coding: utf-8 -*-

import numpy as np
import tensorflow.keras.backend as K
import pickle


def masked_mse(y_true, y_pred, V):

    mmse = K.sum(y_true[:, V:]*(y_true[:, :V]-y_pred)**2, axis=-1)
    s = 0
    for i in mmse:
        s += i
    return s/len(mmse)


data_path = 'forecasting_preds_test.pkl'
data, var_to_ind = pickle.load(open(data_path, 'rb'))

y_true = []
for y in data['forecasting_test_op']:
    y_true.append(y)
y_true = np.array(y_true)


y_pred = []
for y in data['forecasting_pred']:
    y_pred.append(y)
y_pred = np.array(y_pred)
