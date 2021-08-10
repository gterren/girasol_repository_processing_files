from datetime import datetime
from scipy.interpolate import interp1d

import numpy as np
import glob, os, shutil


def _load_files(file): return np.loadtxt(file, delimiter = ',')

def _images_continous_adquisition(T_, t_inc = 15.):
    c = (np.diff(T_[0, :]) > t_inc ).sum()
    if c == 0.: return True
    else: return False

# Copy Infrared Images
def _copy_images(X_, name_, path_in, path_out):
    name = r'{}/{}'.format(path_out, name_[-10:])
    if not os.path.exists(name): os.mkdir(name)

    for file in X_:
        file_out = file.replace(path_in[:-1], path_out)
        if not os.path.exists(file_out): shutil.copy(file, file_out)
    print(name)

path_in = r'E:/vi_camera/'
path_out_visible = r'E:/girasol_repository_files/vi_camera'

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

    if _images_continous_adquisition(T_):
        _copy_images(X_, folder, path_in, path_out_visible)
