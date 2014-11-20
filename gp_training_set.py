# Este script ajusta un gp sobre cada curva de la base de datos. 
# Los parametros del GP son elegidos arbitrariamente
# Para cada curva se guarda el valor de las features calculadas para cada muestra en un txt separado

# --------------------------------------------------------------------------
import lightcurves.lc_utils as lu
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import george
from george import kernels
import os, sys

lib_path = os.path.abspath('../time-series-feats')
sys.path.append(lib_path)
from Feature import FeatureSpace

import time
import datetime

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

for i in range(len(paths)):
    start_time = time.time()
    path = paths[i]

    # Para descartar algunas curvas
    if not 'B.mjd' in path:
        continue

    if i in range(2862, 3862):
        continue

    print 'Curva: ' + lu.get_lightcurve_id(path)

    azul = lu.open_lightcurve(paths[i])
    total_days = azul.index[-1] - azul.index[0]

    if len(azul.index) < 500:
        continue

    # Preparo la curva para alimentar el GP
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(azul, 500)
    t_obs = np.ravel(t_obs)
    y_obs = np.ravel(y_obs)
    err_obs = np.ravel(err_obs)

    # Preparo GP
    var = np.var(y_obs)
    l = 6 * (max_time - min_time) / float(total_days)   # son 6 dias segun lo observado en otros ajustes
    kernel = var**2 * kernels.ExpSquaredKernel(l**2)

    gp = george.GP(kernel, mean=np.mean(y_obs))
    gp.compute(t_obs, yerr=err_obs)
    
    # Sampleo curvas del GP
    sys.stdout.write('Sampleando curvas...')
    sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.flush()

    samples = []
    x = np.linspace(min_time, max_time, 500)

    for s in xrange(100):
        # sampleo del modelo sobre la curva original
        m = gp.sample_conditional(y_obs , t_obs)

        # hago una prediccion para obtener la std de la curva sampleada
        mu, cov = gp.predict(m, x)
        sigma = np.sqrt(np.diag(cov))
        samples.append((m, sigma))

    # Calculo algunas features para el grupo de muestras
    sys.stdout.write('Calculando Features...')
    sys.stdout.flush()
    sys.stdout.write('\r')
    sys.stdout.flush()

    feature_names = ['Amplitude', 'Beyond1Std', 'Con', 'MaxSlope', 'MedianAbsDev', 'MedianBRP', 'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std', 'StestonK', 'VariabilityIndex', 'meanvariance']
    feature_values = []

    for s in samples:
        fs = FeatureSpace(featureList=feature_names, Beyond1Std=s[1], MaxSlope=x)
        fs = fs.calculateFeature(s[0])
        feature_values.append( map(lambda x: float("{0:.5f}".format(x)),fs.result(method='')) )

    # Escribo los resultados en un archivo especial para cada curva original
    lc_class = lu.get_lc_class_name(path)
    macho_id = lu.get_lightcurve_id(path)
    file_path = 'GP Samples/' + lc_class + '/' + macho_id + '.txt'

    df = pd.DataFrame(feature_values, columns = feature_names)
    df.to_csv(file_path, index=False)

    end_time = time.time()
    print 'Tiempo tomado por curva: ' + str(datetime.timedelta(0,end_time - start_time))
