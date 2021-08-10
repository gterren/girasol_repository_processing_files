import numpy as np
import glob, os, pickle
from scipy.interpolate import interp1d
from datetime import datetime

def _load_csv(file): return np.loadtxt(file, delimiter = ',')


def _save_files(X_, name_, path_out, extension = '.csv'):

    if not os.path.exists(path_out): os.mkdir(path_out)

    name = '{}/{}{}'.format(path_out, name_[-10:], extension)
    np.savetxt(name, X_, delimiter = ',')
    print(name)

# Function to load images listed in intervals of 15 seconds (k = 1) to 5 min (k = 20)
def _load_files(name):
    files = []
    with open(name, "rb") as f:
        while True:
            try: files.append(pickle.load(f))
            except: break
    return files

## Correct the effects found on the pyranometer due to movement and
## desplancement of the system. I_GSI are sensitive to the inclination
## of the pyranometer.
def _pyranometer_bias(tm_0, tm_1, M_0_):
    # Amplitude bias ciclo-stationary model
    def __periodic_model(M_0_, tm_0, N = 365.):
        return M_0_[0] * np.sin(M_0_[1] + ( (2*np.pi) / N ) * tm_0) + M_0_[2]
    # Pisewise Model with for correlation shiftings
    def __picewise_model(M_0_, tm0, tm1):
        if tm_0 <= M_0_[4]:
            y_1 = M_0_[0]
        if tm_0 >  M_0_[4]:
            y_1 = M_0_[1]
        if tm_0 >  M_0_[5]:
            y_1 = M_0_[2]
        if tm_0 >  M_0_[6] or tm_1 > 2018:
            y_1 = M_0_[3]
        return int(y_1)
    return __periodic_model(M_0_[0], tm_0), __picewise_model(M_0_[1], tm_0, tm_1)

# Apply corrections on amplitude and inclination
def _pyranometer_bias_correction(I_, P_, sigma, x_inc, n, min_elevation = 15.):
    # Physical model with not ground irradiance refletion
    def __GSI_physical_model(X_, n):
        def ___GSI(X_, A, B, C):
            Ib  = A * np.exp( - B/np.sin(np.radians(X_)) )
            Ibc = Ib * np.cos(np.radians(90. - X_))
            Idc = C * Ib
            Ird = 0. #* x0 * Ib * ( np.sin(np.radians(X)) + C )
            return Ibc + Idc + Ird
        # Day of the year GSI model Coeffiecients
        def ___coefficients(n):
            A = 1160. +  75. * np.sin(np.radians( (360./365)*(n - 275.) ))
            B = 0.174 + .035 * np.sin(np.radians( (360./365)*(n - 100.) ))
            C = 0.095 + .04  * np.sin(np.radians( (360./365)*(n - 100.) ))
            return A, B, C

        A, B, C = ___coefficients(n)
        return ___GSI(X_, A, B, C)

    # Correct Amplitude Bias
    i_prime_ = I_[1, :]/sigma
    # Get Variables recording Vector
    t_ = I_[0, :]
    e_ = P_[1, :]
    a_ = P_[2, :]
    # Get Physical Model Estimation
    g_ = __GSI_physical_model(e_, n)
    x_ = np.linspace(0, t_.shape[0], t_.shape[0])
    # Correct signal to aling them at the highest correlation point
    if x_inc < 0:
        x_inc    = abs(x_inc)
        g_shift_ = g_[:-x_inc]
        x_shift_ = x_[x_inc:]
        i_prime_ = i_prime_[x_inc:]
        g_prime_ = g_[x_inc:]
        t_prime_ = t_[x_inc:]
        e_prime_ = e_[x_inc:]
        a_prime_ = a_[x_inc:]
    else:
        x_inc    = abs(x_inc)
        g_shift_ = g_[x_inc:]
        x_shift_ = x_[:-x_inc]
        i_prime_ = i_prime_[:-x_inc]
        g_prime_ = g_[:-x_inc]
        t_prime_ = t_[:-x_inc]
        e_prime_ = e_[:-x_inc]
        a_prime_ = a_[:-x_inc]
    # Detrend Irradiance
    i_detrended_ = i_prime_ / g_shift_
    # Trending Irradiance to correct Inclicination bias
    i_trended_ = i_detrended_ * g_prime_
    # Remove recordings below a minimu sun's elevation angle
    idx_ = e_prime_ > min_elevation
    # Concatenate Data
    I_ = np.concatenate((t_prime_[np.newaxis, idx_], i_trended_[np.newaxis, idx_]), axis = 0)
    P_ = np.concatenate((t_prime_[np.newaxis, idx_], e_prime_[np.newaxis, idx_], a_prime_[np.newaxis, idx_]), axis = 0)
    return I_, P_


path_in_position     = r'E:/girasol_repository_files/sun_position'
path_in_pyranometer  = r'E:/girasol_repository_files/pyranometer'
# Data Out paths
path_out_position    = r'E:/girasol_repository_files/sun_position_v2'
path_out_pyranometer = r'E:/girasol_repository_files/pyranometer_v2'
# Load Model
name = r'pyranometer_bias_model.pkl'
m_   = _load_files('E:/girasol_repository_files/extra/{}'.format(name))[0]
# Variables Initialization
X_ = []
T_ = np.empty((1, 0))
# Loop over files in dir
for py_file, po_file in zip(glob.glob(r'{}/*'.format(path_in_pyranometer)), glob.glob(r'{}/*'.format(path_in_position))):
    print(py_file)
    print(po_file)
    # Load files:
    I_ = _load_csv(py_file).T
    P_ = _load_csv(po_file)
    print(I_.shape, P_.shape)
    # Process UNIX time to get year and year-day
    t_unix     = I_[0, 0]
    t_year_day = datetime.fromtimestamp((t_unix)).timetuple().tm_yday
    t_year     = datetime.fromtimestamp((t_unix)).timetuple().tm_year
    # Correct artifacts produces by pyranometer
    sigma, x_inc = _pyranometer_bias(t_year_day, t_year, m_)
    # Corrrect Pyranometer bias
    I_prime_, P_prime_ = _pyranometer_bias_correction(I_, P_, sigma, x_inc, t_year_day)
    # Save Modification
    _save_files(I_prime_.T, py_file[-14:-4], path_out_pyranometer, extension = '.csv')
    _save_files(P_prime_.T, po_file[-14:-4], path_out_position, extension = '.csv')
