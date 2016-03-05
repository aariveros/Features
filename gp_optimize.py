# coding=utf-8

# Toma una curva de luz ajusta un GP optimizando los parámetros y gráfica el 
# ajuste resultante.
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import scipy.optimize as op
from george import kernels
import numpy as np
import george
import FATS

from functools import partial
import optimize

import lightcurves.lc_utils as lu
import graf

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

file_dir = 'Resultados/Histogramas/ambos/'
catalog = 'MACHO'
percentage = 0.8

paths = lu.get_lightcurve_paths(catalog=catalog, both_bands=True)
for i in [0, 255, 457, 967, 1697, 2862, 12527, 12700]:
    path = paths[i]

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

    partial_op = partial(optimize.nll, gp=gp, y_obs=y_obs)

    print(gp.lnlikelihood(y_obs))
    p0 = gp.kernel.vector
    results = op.minimize(partial_op, p0,  method='Nelder-Mead')

    gp.kernel[:] = results.x
    print(gp.lnlikelihood(y_obs))

    # Grafico el ajuste resultante 
    # -----------------------------------------------------------------------------

    x = np.linspace(np.min(t_obs), np.max(t_obs), 500)
    mu, cov = gp.predict(y_obs, x)
    std = np.sqrt(np.diag(cov))

    plt.figure()

    plt.errorbar(t_obs, y_obs, yerr=err_obs, fmt=".b", ecolor='r', capsize=0)
    graf.graf_GP(x, mu, std)

    plt.show()
    plt.close()