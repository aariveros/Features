# coding=utf-8
# Toma una curva de luz, hace un bootstrap simple calcula features sobre
# las muestras y hace un histograma con ellas
# -----------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import lightcurves.lc_utils as lu
import numpy as np
import random
import bootstrap

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
a, b = 967, 968

azul = lu.open_lightcurve(paths[a])

y_obs = azul['mag']
t_obs = azul.index
err_obs = azul['err']

# Calculo el valor de las features para la curva completa
lista = ['Amplitude', 'Beyond1Std', 'Con', 'MaxSlope', 'MedianAbsDev',
         'MedianBRP', 'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std',
         'StestonK', 'VariabilityIndex', 'meanvariance']
         
fs = FeatureSpace(featureList=lista, Beyond1Std=err_obs, MaxSlope=t_obs)

fs = fs.calculateFeature(y_obs)
real_values = fs.result(method='dict')

samples = bootstrap.uniform_bootstrap(azul, 0.8)
bootstrap_values = []

for lc in samples:
    y_obs = lc['mag']
    t_obs = lc.index
    err_obs = lc['err']

    fs = FeatureSpace(featureList=lista, Beyond1Std=err_obs, MaxSlope=t_obs)

    fs = fs.calculateFeature(y_obs)
    bootstrap_values.append(fs.result(method=''))

aux = pd.DataFrame(bootstrap_values, columns=lista)

plt.figure()
f_name = 'Skew'

values = aux[f_name].tolist()
mean = np.mean(values)
std = np.std(values)
x = np.linspace(mean - 4*std,mean +4*std,100)
plt.plot(x,mlab.normpdf(x,mean,std), 'k--')

n, bins, patches = plt.hist(values, 60, normed=1, histtype='bar', color = 'b', alpha=0.6)
plt.axvline(x= real_values[f_name], color = 'r', label=u'Real value')
plt.show()
plt.close()
