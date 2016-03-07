# coding=utf-8

# Calcula el rmsd de ajustar un gaussian process sobre las curvas de luz
# de un catalogo
# -----------------------------------------------------------------------------

from george import kernels
import numpy as np
import pandas as pd
import george

from functools import partial
import lightcurves.lc_utils as lu

import scipy.optimize as op
import optimize

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

if __name__ == '__main__':

    catalog = 'MACHO'
    percentage = 0.5
    normalize = 'Std'
    param_choice = 'fitted'
    filter_p = 0.2

    paths = lu.get_lightcurve_paths(catalog=catalog)
    paths = lu.stratified_filter(paths, catalog=catalog, percentage=filter_p)

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

        # Inicializo kernel
        var = np.var(y_obs)
        l = 6
        kernel = var * kernels.ExpSquaredKernel(l ** 2)
        
        gp = george.GP(kernel, mean=np.mean(y_obs))
        gp.compute(t_obs, yerr=err_obs)

        partial_op = partial(optimize.nll, gp=gp, y_obs=y_obs)

        p0 = gp.kernel.vector
        results = op.minimize(partial_op, p0,  method='Nelder-Mead')
        gp.kernel[:] = results.x

        # Ajusto el gaussian process a las observaciones de la curva
        mu, cov = gp.predict(y_obs, t_obs)

        rms_errors.append(rms(y_obs, mu, normalize))
        lc_ids.append(lc_id)
        lc_classes.append(lc_class)

    rms_dict = {'rmsd': rms_errors, 'class': lc_classes}
    df = pd.DataFrame(rms_dict, index=lc_ids)
    df.to_csv('/Users/npcastro/Dropbox/Resultados/RMSD/' + param_choice +
              '/50.csv')