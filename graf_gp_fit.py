# coding=utf-8

# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
from george import kernels
import numpy as np
import george

import lightcurves.lc_utils as lu
import graf

catalog = 'MACHO'
percentage = 0.5
lc_id = '1.3320.174'

paths = lu.get_lightcurve_paths(catalog=catalog)

if catalog == 'MACHO':
    paths = [x for x in paths if 'R.mjd' not in x]

path = [x for x in paths if lc_id in x][0]

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
x = np.linspace(np.min(t_obs), np.max(t_obs), 500)
mu, cov = gp.predict(y_obs, x)
std = np.sqrt(np.diag(cov))

plt.figure()

graf.graf_GP(x, mu, std)
plt.errorbar(lc.index, lc['mag'], yerr=lc['err'], fmt=".b", ecolor='r', capsize=0)

plt.title(lc_id + ' - ' + lc_class)
plt.ylabel('Magnitude')
plt.xlabel('MJD')

plt.show()
plt.close()