import numpy as np
import glob, os, pickle
from scipy.interpolate import interp1d
from datetime import datetime
from cv2 import imread, IMREAD_UNCHANGED

from itertools import compress

def _load_infrared(file): return imread(file, IMREAD_UNCHANGED)

def _load_csv(file): return np.loadtxt(file, delimiter = ',')

def _get_commum_dates():

    path_in_position    = r'E:\girasol_repository_files\sun_position'
    path_in_pyranometer = r'E:\girasol_repository_files\pyranometer'
    path_in_infrared    = r'E:\girasol_repository_files\ir_camera'
    path_in_visible     = r'E:\girasol_repository_files\vi_camera'
    path_in_weather     = r'E:\girasol_repository_files\weather_station'

    def __get_dates(files_, i_low, i_high): return [file_[i_low:i_high] for file_ in files_]

    def __check_time_stamps(py_idx_, po_idx_):
        for i, j, k in zip(py_idx_, po_idx_, ws_idx_):
            I_ = _load_csv(py_files_[i])
            P_ = _load_csv(po_files_[j])
            W_ = _load_csv(po_files_[k])
            print(i, j, I_.shape, P_.shape, W_.shape)
            # If the Same diff = 0.
            if ( I_[:, 0] - P_[:, 0] - W_[:, 0]  ).sum() != 0.0: print(diff)

    py_files_ = glob.glob(r'{}\*'.format(path_in_pyranometer))
    po_files_ = glob.glob(r'{}\*'.format(path_in_position))
    ws_files_ = glob.glob(r'{}\*'.format(path_in_weather))
    im_files_ = glob.glob(r'{}\*'.format(path_in_infrared))
    print(len(py_files_), len(po_files_), len(ws_files_), len(im_files_))

    # Get List of Dates in each file
    py_dates_ = __get_dates(py_files_, i_low = -14, i_high = -4)
    po_dates_ = __get_dates(po_files_, i_low = -14, i_high = -4)
    ws_dates_ = __get_dates(ws_files_, i_low = -14, i_high = -4)
    im_dates_ = __get_dates(im_files_, i_low = -10, i_high = None)
    print(len(py_dates_), len(po_dates_), len(ws_dates_), len(im_dates_))

    # Find Commum Elements
    list_1_ = list(set(py_dates_).intersection(po_dates_))
    list_2_ = list(set(py_dates_).intersection(im_dates_))
    list_3_ = list(set(po_dates_).intersection(ws_dates_))
    dates_  = list(set(list_1_).intersection(list_2_))
    dates_  = list(set(dates_).intersection(list_3_))

    # Find Commum Index Elements
    py_idx_ = sorted([py_dates_.index(x) for x in dates_])
    po_idx_ = sorted([po_dates_.index(x) for x in dates_])
    ws_idx_ = sorted([ws_dates_.index(x) for x in dates_])
    im_idx_ = sorted([im_dates_.index(x) for x in dates_])
    print(len(py_idx_), len(po_idx_), len(ws_idx_), len(im_idx_))

    # Position and Pyranometer Time Stamps matches?
    #__check_time_stamps(py_idx_, po_idx_)
    return py_files_, py_idx_, po_files_, po_idx_, ws_files_, ws_idx_, im_files_, im_idx_

def _get_capture_time(py_files_, py_idx_, po_files_, po_idx_, ws_files_, ws_idx_, im_files_, im_idx_):

    def __get_py_timestamps(py_files_, py_idx_):
        X_, Y_ = [], []
        for i in py_idx_:
            print(py_files_[i])
            I_ = _load_csv(py_files_[i])
            X_.append(I_[:, 0])
            Y_.append(I_[:, 1])
        return X_, Y_

    def __get_po_timestamps(po_files_, po_idx_):
        X_, Y_, Z_ = [], [], []
        for i in po_idx_:
            print(po_files_[i])
            P_ = _load_csv(po_files_[i])
            X_.append(P_[:, 0])
            Y_.append(P_[:, 1])
            Z_.append(P_[:, 2])
        return X_, Y_, Z_

    def __get_ws_timestamps(ws_files_, ws_idx_):
        X_, T_, D_, P_, A_, M_, H_ = [], [], [], [], [], [], []
        for i in ws_idx_:
            print(ws_files_[i])
            W_ = _load_csv(ws_files_[i])
            X_.append(W_[:, 0])
            T_.append(W_[:, 1])
            D_.append(W_[:, 2])
            P_.append(W_[:, 3])
            A_.append(W_[:, 4])
            M_.append(W_[:, 5])
            H_.append(W_[:, 6])
        return X_, T_, D_, P_, A_, M_, H_

    def __get_im_timestamps(im_files_, im_idx_):
        X_, Y_ = [], []
        for i in im_idx_:
            print(im_files_[i])
            # Get files names
            im_names_ = glob.glob(r'{}/*'.format(im_files_[i]))
            im_times_ = np.zeros((len(im_names_)))
            y_ = []
            for i in range(len(im_names_)):
                im_times_[i] = float(im_names_[i][-16:-6])
                y = _load_infrared(im_names_[i])
                y_.append(y)
            X_.append(im_times_)
            Y_.append(y_)
        return X_, Y_

    # Get pyranometer-resolution time Stamps
    py_t_, py_y_ = __get_py_timestamps(py_files_, py_idx_)
    print(len(py_t_), len(py_y_))
    po_t_, po_y_, po_z_ = __get_po_timestamps(po_files_, po_idx_)
    print(len(po_t_), len(po_y_), len(po_z_))
    ws_t_, ws_y_, ws_d_, ws_p_, ws_a_, ws_m_, ws_h_ = __get_ws_timestamps(ws_files_, ws_idx_)
    print(len(ws_t_), len(ws_y_), len(ws_d_), len(ws_p_), len(ws_a_), len(ws_m_), len(ws_h_))
    # Get infrared-resolution time Stamps
    im_t_, im_y_ = __get_im_timestamps(im_files_, im_idx_)
    print(len(im_t_), len(im_y_))

    print(py_t_[0].shape, py_y_[0].shape)
    print(po_t_[0].shape, po_y_[0].shape, po_z_[0].shape)
    print(ws_t_[0].shape, ws_y_[0].shape, ws_d_[0].shape, ws_p_[0].shape, ws_a_[0].shape, ws_m_[0].shape, ws_h_[0].shape)
    print(im_t_[0].shape)

    return py_t_, py_y_, po_t_, po_y_, po_z_, ws_t_, ws_y_, ws_d_, ws_p_, ws_m_, ws_a_, ws_h_, im_t_, im_y_


def _get_mean_time(py_t_, py_y_, po_t_, po_y_, po_z_, ws_t_, ws_y_, ws_d_, ws_p_, ws_a_, ws_m_, ws_h_, im_t_, im_y_):

    py_int_Y_, po_int_Y_, po_int_Z_, ws_int_T_, ws_int_D_, ws_int_P_, ws_int_A_, ws_int_M_, ws_int_H_ = [], [], [], [], [], [], [], [], []

    for k in range(len(im_t_)):
        N = im_t_[k].shape[0]
        print(py_files_[k])
        print(po_files_[k])
        print(ws_files_[k])

        py_int_y_ = np.zeros((N))

        po_int_y_ = np.zeros((N))
        po_int_z_ = np.zeros((N))

        ws_int_t_ = np.zeros((N))
        ws_int_d_ = np.zeros((N))
        ws_int_p_ = np.zeros((N))
        ws_int_a_ = np.zeros((N))
        ws_int_m_ = np.zeros((N))
        ws_int_h_ = np.zeros((N))

        for i in range(N):
            if i == 0:
                idx_ = py_t_[k] < im_t_[k][i]
            if i == N - 1:
                idx_ = py_t_[k] > im_t_[k][i]
            if i != 0 and i != N - 1:
                idx_1 = py_t_[k] > im_t_[k][i - 1]
                idx_2 = py_t_[k] < im_t_[k][i]
                idx_ = idx_1 & idx_2

            py_int_y_[i] = np.mean(py_y_[k][idx_])
            po_int_y_[i] = np.mean(po_y_[k][idx_])

            po_int_z_[i] = np.mean(po_z_[k][idx_])

            ws_int_t_[i] = np.mean(ws_y_[k][idx_])
            ws_int_d_[i] = np.mean(ws_d_[k][idx_])
            ws_int_p_[i] = np.mean(ws_p_[k][idx_])
            ws_int_a_[i] = np.mean(ws_a_[k][idx_])
            ws_int_m_[i] = np.mean(ws_m_[k][idx_])
            ws_int_h_[i] = np.mean(ws_h_[k][idx_])

        py_int_Y_.append(py_int_y_)

        po_int_Y_.append(po_int_y_)
        po_int_Z_.append(po_int_z_)

        ws_int_T_.append(ws_int_t_)
        ws_int_D_.append(ws_int_d_)
        ws_int_P_.append(ws_int_p_)
        ws_int_A_.append(ws_int_a_)
        ws_int_M_.append(ws_int_m_)
        ws_int_H_.append(ws_int_h_)

    print(len(py_int_Y_), len(po_int_Y_), len(po_int_Z_), len(ws_int_T_), len(ws_int_D_), len(ws_int_P_), len(ws_int_A_), len(ws_int_M_), len(ws_int_H_))

    return py_int_Y_, po_int_Y_, po_int_Z_, ws_int_T_, ws_int_D_, ws_int_P_, ws_int_A_, ws_int_M_, ws_int_H_

def _get_detrented_irradiance(py_files_, py_t_, py_int_Y_, po_files_, po_int_Y_):

    # Physical model with not ground irradiance refletion
    def __GSI_physical_model(X_, n):
        def __GSI(X_, A, B, C):
                Ib  = A * np.exp( - B/np.sin(np.radians(X_)) )
                Ibc = Ib * np.cos(np.radians(90. - X_))
                Idc = C * Ib
                Ird = 0. #* x0 * Ib * ( np.sin(np.radians(X)) + C )
                return Ibc + Idc + Ird
        # Day of the year GSI model Coeffiecients
        def __coefficients(n):
            A = 1160. +  75. * np.sin(np.radians( (360./365)*(n - 275.) ))
            B = 0.174 + .035 * np.sin(np.radians( (360./365)*(n - 100.) ))
            C = 0.095 + .04  * np.sin(np.radians( (360./365)*(n - 100.) ))
            return A, B, C

        A, B, C = __coefficients(n)
        return __GSI(X_, A, B, C)

    # Calculate Clear Sky Index with corrected elevation
    def __CSI(f_, g_): return f_ / g_

    py_int_Z_, py_int_W_ = [], []

    for k in range(len(im_t_)):
        print(py_files_[k])
        print(po_files_[k])

        # Get Variables recording Vector
        t_ = py_t_[k][0]
        f_ = py_int_Y_[k]
        e_ = po_int_Y_[k]
        print(t_, f_.shape, e_.shape)
        # Process UNIX time to get year and year-day
        t_unix     = t_
        t_year_day = datetime.fromtimestamp((t_unix)).timetuple().tm_yday
        t_year     = datetime.fromtimestamp((t_unix)).timetuple().tm_year
        # Get Physical Model Estimation
        g_ = __GSI_physical_model(e_, t_year_day)
        # Calculate Clear Sky Index
        w_ = __CSI(f_, g_)

        py_int_Z_.append(g_)
        py_int_W_.append(w_)

    return py_int_Z_, py_int_W_


def _get_elevation_samples(PY_, PO_, WS_, IM_):

    def __max_ele_angle(x_, max_elevation = 20.):
        return x_ > max_elevation

    def __remove_index_samples(X_, idx_, i):
        Y_ = []
        for x_ in X_:
            y_ = list(compress(x_[i], idx_))
            print(len(y_))
            Y_.append(y_)
        return Y_

        print(len(PY_), len(PO_), len(WS_), len(IM_), len(IM_[0]))

    py_, po_, ws_, im_ = [], [], [], []

    for i in range(len(IM_[0])):
        idx_ = __max_ele_angle(x_ = PO_[0][i], max_elevation = 21.)

        py_.append(__remove_index_samples(PY_, idx_, i))
        po_.append(__remove_index_samples(PO_, idx_, i))
        ws_.append(__remove_index_samples(WS_, idx_, i))
        im_.append(__remove_index_samples(IM_, idx_, i))

        print(len(py_), len(po_), len(ws_), len(im_))

    print(len(py_), len(po_), len(ws_), len(im_))

    return py_, po_, ws_, im_

def _get_pickle_file(py_files_, py_, po_, ws_, im_, path):

    def __save_data(X_, name):
        with open(name, 'wb') as f: pickle.dump(X_, f)

    for i in range(len(py_)):
        name = py_files_[i][-14:-4]
        name = r'{}\{}.pkl'.format(path, name)
        print(name)
        __save_data(X_ = [py_[i], po_[i], ws_[i], im_[i]], name = name)


py_files_, py_idx_, po_files_, po_idx_, ws_files_, ws_idx_, im_files_, im_idx_ = _get_commum_dates()

py_t_, py_y_, po_t_, po_y_, po_z_, ws_t_, ws_y_, ws_d_, ws_p_, ws_m_, ws_a_, ws_h_, im_t_, im_y_ = _get_capture_time(py_files_, py_idx_, po_files_, po_idx_, ws_files_, ws_idx_, im_files_, im_idx_)

py_int_Y_, po_int_Y_, po_int_Z_, ws_int_T_, ws_int_D_, ws_int_P_, ws_int_A_, ws_int_M_, ws_int_H_ = _get_mean_time(py_t_, py_y_, po_t_, po_y_, po_z_, ws_t_, ws_y_, ws_d_, ws_p_, ws_a_, ws_m_, ws_h_, im_t_, im_y_)

py_int_Z_, py_int_W_ = _get_detrented_irradiance(py_files_, py_t_, py_int_Y_, po_files_, po_int_Y_)

py_, po_, ws_, im_ = _get_elevation_samples(PY_ = [py_int_Y_, py_int_Z_, py_int_W_], PO_ = [po_int_Y_, po_int_Z_],  WS_ = [ws_int_T_, ws_int_D_, ws_int_P_, ws_int_A_, ws_int_M_, ws_int_H_], IM_ = [im_t_, im_y_])

_get_pickle_file(py_files_, py_, po_, ws_, im_, path = r'E:\pickle_data_v4')
