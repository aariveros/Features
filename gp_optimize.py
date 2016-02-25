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



# Grafico el ajuste resultante 
# -----------------------------------------------------------------------------

x = np.linspace(np.min(t_obs), np.max(t_obs), 500)
mu, cov = gp.predict(y_obs, x)
std = np.sqrt(np.diag(cov))

# Mapeo devuelta a los valores originales
mu = mu * lc['mag'].std() + lc['mag'].mean() 
y_obs = y_obs * lc['mag'].std() + lc['mag'].mean() 
std = std * lc['err'].std() + lc['err'].mean()
err_obs = err_obs * lc['err'].std() + lc['err'].mean()
t_obs = t_obs * np.std(lc.index) + np.mean(lc.index) 
x = x * np.std(lc.index) + np.mean(lc.index)

plt.figure()

plt.errorbar(t_obs, y_obs, yerr=err_obs, fmt=".b", ecolor='r', capsize=0)
graf.graf_GP(x, mu, std)

plt.show()
plt.close()