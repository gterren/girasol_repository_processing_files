# To do list:
# - Select Only the Necessary Comlumns
# - Transform time to unix times
# - Transform temperature in F. to celsius
# - Interpolar the data that is missing to 1 second resoluction
# - Check if any day in the girasol machine is not download yet
# - Either download it or remove them
# - Get Starting and ending data of the recording 2017_12_07-2019_01_18
# - Set code in functions
# - Make it rebust so it does not break in case of no existing data for a day
# - Lunch processing for all data

import csv
import requests
import time
import datetime

import numpy as np
import matplotlib.pylab as plt

from scipy import interpolate
import os

# Interpolation
def _interpolate_csv_columns(X_, Y_):
    x_ = X_[:, 0]
    # Variables Initialization
    x_p_ = Y_[:, 0]
    X_p_ = np.zeros((x_p_.shape[0], X_.shape[1]))
    X_p_[:, 0] = x_p_
    for idx in range(1, X_.shape[1]):
        y_ = X_[:, idx]
        _f = interpolate.interp1d(x_, y_, kind = 'linear')
        y_p_ = _f(x_p_)
        X_p_[:, idx] = y_p_
    return X_p_
# Load csv file
def _load_csv_file(path):
    return np.loadtxt(open(path, "rb"), delimiter = ",")
# Save it back to the csv file
def _save_csv_file(X_p_, path):
    return np.savetxt(path, X_p_, delimiter = ",")


path_iws = r'E:\weather_station'
path_opy = r'E:\girasol_repository_files\pyranometer'
path_ows = r'E:\girasol_repository_files\weather_station'

for file in os.listdir(path_opy):
    file_ws = '{}\{}'.format(path_iws, file)
    file_py = '{}\{}'.format(path_opy, file)
    X_ = _load_csv_file(file_ws)
    Y_ = _load_csv_file(file_py)
    X_p_ = _interpolate_csv_columns(X_, Y_)
    print(X_.shape, X_p_.shape, Y_.shape)
    path = '{}\{}'.format(path_ows, file)
    _save_csv_file(X_p_, path)
    print(path)
