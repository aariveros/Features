# coding=utf-8
# Toma una curva de luz, hace un bootstrap calcula features sobre
# las muestras y hace un histograma con ellas
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
from george import kernels
import pandas as pd
import numpy as np
import george
import FATS

import lightcurves.lc_utils as lu
import graf
import bootstrap

def calc_bootstrap(lc, kernel, sampling, feature_list):
    samples_devs = bootstrap.GP_bootstrap(lc, kernel, sampling=sampling)
    t_obs = samples_devs[0]
    samples = samples_devs[1]
    bootstrap_values = []

    for s in samples:
        y_obs = s[0]
        err_obs = s[1]

        fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                           featureList=feature_list, excludeList=None)

        fs = fs.calculateFeature([y_obs, t_obs, err_obs])
        bootstrap_values.append(map(lambda x: float("{0:.6f}".format(x)),
                                    fs.result(method='')))
    return bootstrap_values


catalog = 'MACHO'
percentage = 0.5
lc_id = '2.5025.10'
sampling = 'equal'
param_choice = 'set'
file_dir = '/Users/npcastro/Desktop/histograms/' + sampling + '/' + param_choice + '/'

paths = lu.get_lightcurve_paths(catalog=catalog)
if catalog == 'MACHO':
    paths = [x for x in paths if 'R.mjd' not in x]

path = [x for x in paths if lc_id in x][0]

lc_class = lu.get_lightcurve_class(path, catalog=catalog)

lc = lu.open_lightcurve(path, catalog=catalog)
lc = lu.filter_data(lc)
lc = lc.iloc[0:int(percentage * lc.index.size)]

t_obs = lc.index.tolist()
y_obs = lc['mag'].tolist()
err_obs = lc['err'].tolist()

# Calculo el valor de las features para la curva completa
feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
                'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
                'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'Q31', 'Rcs', 'Skew',
                'SlottedA_length', 'SmallKurtosis', 'Std', 'StetsonK', 'StetsonK_AC']
         
fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                       featureList=feature_list, excludeList=None)

fs = fs.calculateFeature([y_obs, t_obs, err_obs])
real_values = fs.result(method='dict')

# Preparo la curva para alimentar el GP
t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

# Preparo GP, l son 6 dias segun lo observado en otros papers
var = np.var(y_obs)
l = 6
kernel = var * kernels.ExpSquaredKernel(l ** 2)
gp = george.GP(kernel, mean=np.mean(y_obs))
gp.compute(t_obs, yerr=err_obs)

sampled_values = calc_bootstrap(lc, kernel, sampling, feature_list)
sampled_df = pd.DataFrame(sampled_values, columns=feature_list)


for f_name in feature_list:
    real_value = real_values[f_name].tolist()
    sampled_values = sampled_df[f_name].tolist()
    
    fig = plt.figure(f_name)
    ax = fig.add_subplot(111)
    
    graf.graf_hist(sampled_values, 'sampled')

    plt.axvline(x=real_value, color = 'r', label=u'Real value', linewidth=2.0)

    plt.ylabel('Count')
    plt.xlabel('Feature Value')
    
    plt.title(f_name)
    plt.legend()

    plt.savefig(file_dir + f_name + '.png')
    plt.close()
