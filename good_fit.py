# coding=utf-8

# -----------------------------------------------------------------------------

from george import kernels
import numpy as np
import pandas as pd
import george
import FATS
import lightcurves.lc_utils as lu
import bootstrap

def rms(true_values, sampled_values, normalize=''):
    """
    """
    n = len(sampled_values)
    aux = (true_values - sampled_values) ** 2
    aux = np.sqrt(sum(aux) / n)
    
    if normalize == '':
        return aux
    elif normalize == 'Mean':
        return aux / np.mean(true_values)
    elif normalize == 'Range':
        rango = np.max(true_values) - np.min(true_values)
        return aux / rango
    elif normalize == 'Std':
        return aux / np.std(true_values)

catalog = 'MACHO'
percentage = 0.5
normalize = 'Std'

paths = lu.get_lightcurve_paths(catalog=catalog)

lc_ids = []
rms_errors = []
lc_classes = []

count = 0
for path in paths:
    print count
    count +=1

    lc_id = lu.get_lightcurve_id(path, catalog=catalog)
    lc_class = lu.get_lightcurve_class(path, catalog=catalog)

    lc = lu.open_lightcurve(path, catalog=catalog)
    lc = lu.filter_data(lc)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    # Preparo la curva para alimentar el GP
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

    # Preparo GP, l son 6 dias segun lo observado en otros papers
    var = np.var(y_obs)
    l = 6 * (max_time - min_time) / float(lc.index[-1] - lc.index[0])

    kernel = var * kernels.ExpSquaredKernel(l ** 2)
    
    gp = george.GP(kernel, mean=np.mean(y_obs))
    gp.compute(t_obs, yerr=err_obs)

    # Ajusto el gaussian process a las observaciones de la curva
    mu, cov = gp.predict(y_obs, t_obs)

    rms_errors.append(rms(y_obs, mu, normalize))
    lc_ids.append(lc_id)
    lc_classes.append(lc_class)


