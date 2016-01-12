# coding=utf-8
# Toma una curva de luz, hace un bootstrap calcula features sobre
# las muestras y hace un histograma con ellas
# -----------------------------------------------------------------------------

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import lightcurves.macho_utils as lu
import numpy as np

import bootstrap

import FATS

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

def graf_hist(f_name, sampled_values, real_values):
	plt.figure()

	values = sampled_values[f_name].tolist()
	mean = np.mean(values)
	std = np.std(values)
	x = np.linspace(mean - 4 * std, mean + 4 * std, 100)
	plt.plot(x, mlab.normpdf(x, mean, std), 'k--')

	n, bins, patches = plt.hist(values, 60, normed=1, histtype='bar', color = 'b', alpha=0.6)
	plt.axvline(x= real_values[f_name], color = 'r', label=u'Real value')
	plt.show()
	plt.close()

paths = lu.get_lightcurve_paths()
path = paths[967]
azul = lu.open_lightcurve(path)
azul = lu.filter_data(azul)

t_obs = azul.index.tolist()
y_obs = azul['mag'].tolist()
err_obs = azul['err'].tolist()

# Calculo el valor de las features para la curva completa
feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
         		'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
         		'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'Q31', 'Rcs', 'Skew',
         		'SlottedA_length', 'SmallKurtosis', 'Std', 'StetsonK', 'StetsonK_AC']
         
fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                       featureList=feature_list, excludeList=None)

fs = fs.calculateFeature([y_obs, t_obs, err_obs])
real_values = fs.result(method='dict')

bootstrap.graf_GP(path, 0.8)

# samples_devs = bootstrap.GP_bootstrap(path, 0.8)
# t_obs = samples_devs[0]
# samples = samples_devs[1]
# bootstrap_values = []

# for s in samples:
#     y_obs = s[0]
#     err_obs = s[1]

#     fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
#                        featureList=feature_list, excludeList=None)

#     fs = fs.calculateFeature([y_obs, t_obs, err_obs])
#     bootstrap_values.append(map(lambda x: float("{0:.6f}".format(x)),
#     							fs.result(method='')))

# df = pd.DataFrame(bootstrap_values, columns=feature_list)

# graf_hist('Mean', df, real_values)
