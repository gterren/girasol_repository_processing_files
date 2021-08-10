import numpy as np
import glob, os, pickle
from scipy.interpolate import interp1d
from datetime import datetime

def _load_csv(file): return np.loadtxt(file, delimiter = ',')

def _remove_images(path, folder, t_min, t_max):
    try:
        files_  = glob.glob(r'{}/{}/*'.format(path, folder))
        N_files = len(files_)
        u_ = np.zeros((N_files))

        for i in range(N_files): u_[i] = float(files_[i][-16:-6])

        idx_ = (u_ < t_min) | (u_ > t_max)
        print('Files Remove: ', idx_.sum())
        for i in np.arange(N_files, dtype = int)[idx_]: os.remove(files_[i])
    except: pass

path_in_position    = r'E:/girasol_repository_files/sun_position_v2'
path_in_pyranometer = r'E:/girasol_repository_files/pyranometer_v2'
path_in_infrared    = r'E:/girasol_repository_files/ir_camera'
path_in_visible     = r'E:/girasol_repository_files/vi_camera'
# Loop over files in dir
for py_file, po_file in zip(glob.glob(r'{}/*'.format(path_in_pyranometer)), glob.glob(r'{}/*'.format(path_in_position))):
    print(py_file)
    print(po_file)
    # Load files:
    I_ = _load_csv(py_file).T
    P_ = _load_csv(po_file).T
    # Get date and times stampts
    file = py_file[-14:-4]
    t_ = I_[0, :]
    print(file, t_[0], t_[-1])
    # Remove Infrared Images
    _remove_images(path_in_infrared, file, t_min = t_[0], t_max = t_[-1])
    # Remove Infrared Visible
    _remove_images(path_in_visible, file, t_min = t_[0], t_max = t_[-1])
