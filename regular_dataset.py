# Este script calcula un set de features para cada curva de la base de datos macho
# Y arma un set de entrenamiento con los valores

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
n_points = 300
feature_values = []

for i in range(len(paths)):
    try:
        path = paths[i]

        # Descarto la banda roja por ahora
        if not 'B.mjd' in path:
            continue

        # No incluyo todas las no variables, ni tampoco unas mirolensings que se me cayeron corriendo los gp
        # if i in range(3562, 12526) or i in range(2778, 2862):
        #     continue

        print 'Curva: ' + lu.get_lightcurve_id(path)

        azul = lu.open_lightcurve(path)

        # Tomo el 60% de las mediciones
        azul = azul.iloc[0:len(azul) * 6 / 10]
        total_days = azul.index[-1] - azul.index[0]
     
        if len(azul.index) < n_points:
            continue

        # Preparo la curva para alimentar el GP
        t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(azul, n_points)
        t_obs = np.ravel(t_obs)
        y_obs = np.ravel(y_obs)
        err_obs = np.ravel(err_obs)

        # Calculo algunas features para el grupo de muestras
        sys.stdout.write('Calculando Features...')
        sys.stdout.flush()
        sys.stdout.write('\r')
        sys.stdout.flush()

        feature_names = ['Amplitude', 'Beyond1Std', 'Con', 'MaxSlope', 'MedianAbsDev', 'MedianBRP', 'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std', 'StetsonK', 'Eta_e', 'Meanvariance']

        fs = FeatureSpace(featureList=feature_names, Beyond1Std=err_obs, MaxSlope=t_obs, Eta_e=t_obs)
        fs = fs.calculateFeature(y_obs)

        clase = lu.get_lc_class_name(path)
        valores = map(lambda x: float("{0:.5f}".format(x)),fs.result(method=''))
        valores.append(clase)

        feature_values.append(valores)
    except KeyboardInterrupt:
        raise
    except:
        continue

feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names)
df.to_csv('macho_60.csv', index=False)