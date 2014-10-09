import pandas as pd
import matplotlib.pyplot as plt
import lightcurves.lc_utils as lu
import numpy as np
import random

import os, sys
lib_path = os.path.abspath('../time-series-feats')
sys.path.append(lib_path)
from Feature import FeatureSpace

def bootstrap_sample(lc, percentage, num_samples=100):
    """Toma una curva de luz y retorna varias muestras aleatorias tomadas de esta
    """

    num_points = len(lc.index)
    samples_size = int(num_points * percentage)

    random.seed(1)

    samples = []

    for i in xrange(num_samples):
        rand_indices = random.sample(range(0,num_points),samples_size)
        rand_indices.sort()
        samples.append(lc.iloc[rand_indices])

    return samples

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
#roja = lu.open_lightcurve(paths[b])
#curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')

y_obs = azul['mag']
t_obs = azul.index
err_obs = azul['err']

# Calculo el valor de las features para la curva completa
lista = ['Amplitude', 'Beyond1Std', 'Con', 'MaxSlope', 'MedianAbsDev', 'MedianBRP', 'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std', 'StestonK', 'VariabilityIndex', 'meanvariance']
fs = FeatureSpace(featureList=lista, Beyond1Std=err_obs, MaxSlope=t_obs)

fs = fs.calculateFeature(y_obs)
real_values = fs.result(method='dict')

samples = bootstrap_sample(azul, 0.8)
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
n, bins, patches = plt.hist(aux['StestonK'].tolist(), 25, normed=1, histtype='bar', color = 'b', alpha=0.6)
plt.axvline(x= real_values['StestonK'], color = 'r', label=u'Real value')
plt.show()
plt.close()
