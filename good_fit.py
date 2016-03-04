# coding=utf-8

# -----------------------------------------------------------------------------

from george import kernels
import numpy as np
import pandas as pd
import george

import lightcurves.lc_utils as lu

import scipy.optimize as op

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
param_choice = 'fitted'
filter_p = 0.2

paths = lu.get_lightcurve_paths(catalog=catalog)
if catalog == 'MACHO':
    paths = [x for x in paths if 'R.mjd' not in x]

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

    # Preparo GP, l son 6 dias segun lo observado en otros papers
    var = np.var(y_obs)
    l = 6
    kernel = var * kernels.ExpSquaredKernel(l ** 2)
    
    gp = george.GP(kernel, mean=np.mean(y_obs))
    gp.compute(t_obs, yerr=err_obs)

    # Defino la función objetivo (negative log-likelihood in this case).
    def nll(p):
        """
        gp: objeto de gaussian process
        y: observaciones sobre las que se ajusta el modelo
        p: parametros sobre los que se quiere optimizar el modelo
        """
        # Update the kernel parameters and compute the likelihood.
        gp.kernel[:] = p
        ll = gp.lnlikelihood(y_obs, quiet=True)

        # The scipy optimizer doesn't play well with infinities.
        return -ll if np.isfinite(ll) else 1e25

    def grad_nll(p):
        # Update the kernel parameters and compute the likelihood.
        gp.kernel[:] = p
        return -gp.grad_lnlikelihood(y_obs, quiet=True)

    gp.compute(t_obs, yerr=err_obs)

    p0 = gp.kernel.vector
    results = op.minimize(nll, p0,  method='Nelder-Mead')

    gp.kernel[:] = results.x

    # Ajusto el gaussian process a las observaciones de la curva
    mu, cov = gp.predict(y_obs, t_obs)

    rms_errors.append(rms(y_obs, mu, normalize))
    lc_ids.append(lc_id)
    lc_classes.append(lc_class)

rms_dict = {'rmsd': rms_errors, 'class': lc_classes}
df = pd.DataFrame(rms_dict, index=lc_ids)
df.to_csv('/Users/npcastro/Dropbox/Resultados/RMSD/' + param_choice +
          '/50%/l-' + str(l) + '.csv')
