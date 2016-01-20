# coding=utf-8
# Toma una curva de luz, hace un bootstrap calcula features sobre
# las muestras y hace un histograma con ellas
# -----------------------------------------------------------------------------

import scipy.optimize as op
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from george import kernels
import pandas as pd
import numpy as np
import george
import FATS

import lightcurves.lc_utils as lu
import bootstrap

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

paths = lu.get_lightcurve_paths(catalog=catalog)
# path = paths[12700]
# path = paths[967]
path = paths[0]

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
l = 6 * (max_time - min_time) / float(lc.index[-1] - lc.index[0])
kernel = kernels.ExpSquaredKernel(l ** 2)

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

print(gp.lnlikelihood(y_obs))
p0 = gp.kernel.vector
results = op.minimize(nll, p0,  method='Nelder-Mead')

gp.kernel[:] = results.x
print(gp.lnlikelihood(y_obs))

bootstrap.graf_GP(lc, gp.kernel)