# Este script calcula todas las features programadas en la libreria de 
# Timeseries para las curva de macho

import lightcurves.lc_utils as lu
import pandas as pd
import numpy as np
import os, sys

lib_path = os.path.abspath('../time-series-feats')
sys.path.append(lib_path)
from Feature import FeatureSpace

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL


paths = lu.get_lightcurve_paths()

# Restriccion de minimo numero de observaciones
# n_points = 300
feature_values = []

for i in range(len(paths)):
    try:

        # Me salto las bandas rojas, y las curvas azules sin banda roja
        if not lu.has_both_bands(path):
            continue

        print 'Curva: ' + lu.get_lightcurve_id(path)

        azul = lu.open_lightcurve(path)
        roja = lu.open_lightcurve(path.replace('B.mjd', 'R.mjd'))

        # if len(azul.index) < n_points:
        #     continue

        # Preparo las curva
        t_obs, y_obs, err_obs = azul.index.tolist(), azul.mag.tolist(), azul.err.tolist()
        t_obs2, y_obs2, err_obs2 = roja.index, roja.mag.tolist(), roja.err.tolist()


        feature_names = ['Amplitude', 'Con', 'MaxSlope', 'MedianAbsDev', 'MedianBRP',
                         'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std', 'StetsonK',
                         'Eta_e', 'Meanvariance']

        fs = FeatureSpace(featureList=feature_names, Beyond1Std=err_obs, MaxSlope=t_obs, Eta_e=t_obs)
        fs = fs.calculateFeature(y_obs)