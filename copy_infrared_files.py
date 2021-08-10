from numpy import array, sin, cos, pi, arccos, arcsin, tan, savetxt, zeros, radians, degrees, vstack, hstack
from time import time, localtime, mktime
from datetime import datetime
from cv2 import imread, IMREAD_UNCHANGED
from scipy.interpolate import interp1d

import numpy as np
import glob, os, shutil


def _load_infrared(file): return imread(file, IMREAD_UNCHANGED)

def _images_continous_adquisition(T_, t_inc = 15.):
    c = (np.diff(T_[0, :]) > t_inc ).sum()
    if c == 0.: return True
    else: return False

# Copy Infrared Images
def _copy_images(X_, name_, path_in, path_out):
    name = r'{}/{}'.format(path_out, name_[-10:])
    if not os.path.exists(name): os.mkdir(name)

    for file in X_: shutil.copy(file, file.replace(path_in[:-1], path_out))
    print(name)


path_in = r'E:/ir_camera/'
path_out_infrared = r'E:/girasol_repository_files/ir_camera'

for folder in glob.glob('{}*'.format(path_in)):
    print(folder)
    # Variables Initialization
    X_ = []
    T_ = np.empty((1, 0))
    for file in glob.glob('{}/*'.format(folder)):
        # * Get files names
        if file.endswith('.png'):
            X_.append(file)
            T_ = np.concatenate((T_, np.array(float(file[-16:-6]))[np.newaxis, np.newaxis]), axis = 1)

    # Verify that adquision as being continuous
    if _images_continous_adquisition(T_):
        _copy_images(X_, folder, path_in, path_out_infrared)
