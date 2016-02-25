# coding=utf-8
# Toma una curva de luz, hace un bootstrap calcula features sobre
# las muestras y hace un histograma con ellas
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
from george import kernels
import numpy as np
import george
import FATS

import lightcurves.lc_utils as lu
import graf
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

# file_dir = 'Resultados/Histogramas/ambos/'
# file_dir = '/Users/npcastro/Dropbox/Tesis NC/Graficos/histogramas/'
file_dir = '/Users/npcastro/Dropbox/Tesis NC/Graficos/GP/'
catalog = 'MACHO'
percentage = 0.5

paths = lu.get_lightcurve_paths(catalog=catalog)

for i in [0, 255, 457, 967, 1697, 2862, 12527, 12700]:
# for i in [2862, 3000, 4000, 5000, 6000]:
    path = paths[i]
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

    # # Desnormalizo los valores
    # mu = mu * lc['mag'].std() + lc['mag'].mean() 
    # std = std * lc['err'].std() + lc['err'].mean()
    # x = x * np.std(lc.index) + np.mean(lc.index)

    plt.figure()

    graf.graf_GP(x, mu, std)
    plt.errorbar(lc.index, lc['mag'], yerr=lc['err'], fmt=".b", ecolor='r', capsize=0)

    plt.title(lc_class)
    plt.ylabel('Magnitude')
    plt.xlabel('MJD')

    plt.show()
    # plt.savefig(file_dir + lc_id + '.png')
    plt.close()