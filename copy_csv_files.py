from numpy import array, sin, cos, pi, arccos, arcsin, tan, savetxt, zeros, radians, degrees, vstack, hstack
from time import time, localtime, mktime
from datetime import datetime
from cv2 import imread, IMREAD_UNCHANGED
from scipy.interpolate import interp1d

import numpy as np
import glob, os, shutil

os.environ['TZ'] = 'America/Denver'

def unixTime(DT, HT):
    #HT = getTime()
    RT = regTime(DT, HT)
    DT = datetime(HT.tm_year, HT.tm_mon, HT.tm_mday, RT[0], RT[1], RT[2])
    UT = int(mktime(DT.timetuple()))
    return UT


def getTime():
    return localtime(time())

def dayLight(GCS, path, HT):
    TC, DA = sunPosition(GCS, path, HT, TCDA = True, save = False)
    GCS    = radians(GCS)
    print(HT)
    SR = 12. - degrees(arccos(-tan(GCS[0]) * tan(DA)))/15. - TC/60.
    SS = 12. + degrees(arccos(-tan(GCS[0]) * tan(DA)))/15. - TC/60.
    return SR, SS


def regTime(DT, HT):
    #HT = getTime()
    hh = divmod(DT, 1)
    mm = divmod(hh[1] * 60., 1)
    ss = divmod(mm[1] * 60., 1)
    return int(hh[0]), int(mm[0]), int(ss[0]), -7 + HT.tm_isdst


def solarTime(GCS, HT): ## CALCULATES SOLAR TIME
    LSTM = 15. * (-7. + HT.tm_isdst)
    B    = radians(360. * (HT.tm_yday - 81) / 365.)
    EOT  = 9.87 * sin(2. * B) - 7.53 * cos(B) - 1.5 * sin(B)
    TC   = 4. * (GCS[1] - LSTM) + EOT
    LST  = HT.tm_hour + HT.tm_min/60. + HT.tm_sec/3600. + TC/60.
    HRA  = 15. * (LST - 12.)
    return LST, HRA, TC


def sunCoordinates(GCS, HT): ## SUN POSITION ANGLES
    LST, HRA, TC = solarTime(GCS, HT)
    GCS = radians(GCS)
    DA  = radians(-23.45) * cos(radians((360./365.)*(HT.tm_yday + 10)))

    EA  = arcsin((sin(GCS[0]) * sin(DA)) + (cos(GCS[0]) * cos(DA) * cos(radians(HRA))))
    AZA = degrees( arccos( ( (sin(DA) * cos(GCS[0])) - (cos(DA) * sin(GCS[0]) * cos(radians(HRA)) )) / cos(EA) ) )
    EA  = degrees(EA)

    if LST > 12.: AZA = 360. - AZA

    return EA, AZA


def _load_files(file): return np.loadtxt(file, delimiter = ',')

def _sun_position(ut_, GCS_ = [35.082089, -106.625905]):
    X_ = np.zeros((3, ut_.shape[0]))
    for i in range(ut_.shape[0]):
        ea, aza = sunCoordinates(GCS_, HT = localtime(ut_[i]))
        X_[0, i] = ut_[i]
        X_[1, i] = ea
        X_[2, i] = aza
    return X_

def _sun_position_interpolation(P_, I_):
    # Interpolation Samples
    n = P_.shape[1]
    N = I_.shape[1]
    # Define sequencias samples of interpolation
    x_      = np.linspace(0, n, n)
    x_star_ = np.linspace(0, n, N)
    # Approximate functions
    _f_0 = interp1d(x_, P_[1, :], kind = 'cubic')
    _f_1 = interp1d(x_, P_[2, :], kind = 'cubic')
    # Interpolation samples
    ea_  = _f_0(x_star_)
    aza_ = _f_1(x_star_)
    return np.concatenate((I_[0, :][:, np.newaxis], ea_[:, np.newaxis], aza_[:, np.newaxis]), axis = 1)

def _pyranometer_continous_adquisition(I_, P_, Y_, t_inc = 1.):
    c = (np.diff(I_[0, :]) > t_inc).sum()
    c+= (np.diff(P_[0, :]) > t_inc).sum()
    c+= (np.diff(Y_[0, :]) > t_inc).sum()
    if c == 0.: return True
    else: return False

# Save Files of pyranometer and sun postion
def _save_files(X_, name_, path_out, extension = '.csv'):

    if not os.path.exists(path_out): os.mkdir(path_out)

    name = r'{}/{}{}'.format(path_out, name_[-14:-4].replace('-','_'), extension)
    np.savetxt(name, X_, delimiter = ',')
    print(name)


path_in = r'E:/pyranometer/'
path_out_position = r'E:/girasol_repository_files/sun_position'
path_out_pyranometer = r'E:/girasol_repository_files/pyranometer'

for file in glob.glob('{}*'.format(path_in)):
    print(file)
    # * load pyranometer recording
    if file.endswith('.csv') and len(file) < 40:
        X_ = _load_files(file)
        # * Estimate Sun's position
        #P_ = _sun_position(ut_ = np.unique(I_[0, :].astype(int)) , GCS_ = [35.082089, -106.625905])
        # * Interpolate Sun's position to match pyranometer readings
        #Z_ = _sun_position_interpolation(P_, I_).T
        # Verify that adquision as being continuous
        #if _pyranometer_continous_adquisition(I_, P_, Z_):
        _save_files(X_.T, file, path_out_pyranometer, extension = '.csv')

path_in = r'E:/sun_position/'
for file in glob.glob('{}*'.format(path_in)):
    print(file)
    # * load pyranometer recording
    if file.endswith('.csv') and len(file) < 40:
        X_ = _load_files(file)
        # * Estimate Sun's position
        #P_ = _sun_position(ut_ = np.unique(I_[0, :].astype(int)) , GCS_ = [35.082089, -106.625905])
        # * Interpolate Sun's position to match pyranometer readings
        #Z_ = _sun_position_interpolation(P_, I_).T
        # Verify that adquision as being continuous
        #if _pyranometer_continous_adquisition(I_, P_, Z_):
        _save_files(X_, file, path_out_position, extension = '.csv')
