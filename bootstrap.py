# coding=utf-8

# Métodos para el desarrollo de bootstraping en series de tiempo
# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
from config import *

import random
import pickle

from george import kernels
import numpy as np
import george


def uniform_bootstrap(lc, percentage, num_samples=100):
    """Toma una curva de luz y retorna varias muestras aleatorias tomadas de
    esta. Para esto hace un muestreo uniforme sin reemplazo.

    percentage: porcentaje de curvas a retornar
    num_samples: numero de muestras a retornar
    """

    num_points = len(lc.index)
    samples_size = int(num_points * percentage)

    random.seed(1)

    samples = []

    for i in xrange(num_samples):
        rand_indices = random.sample(range(0, num_points), samples_size)
        rand_indices.sort()
        samples.append(lc.iloc[rand_indices])

    return samples


def GP_bootstrap(lc_path, percentage=1.0, n_samples=100):
    """Recibe una curva hace un sampleo con un GP sobreajustado
    y retorna las muestras obtenidas

    lc_path: path de la curva de luz
    percentage: porcentaje de la curva a utilizar
    """
    try:
        lc = lu.open_lightcurve(lc_path)
        lc = lc.iloc[0:int(percentage * lc.index.size)]

        total_days = lc.index[-1] - lc.index[0]
        n_points = lc.index.size

        # Preparo la curva para alimentar el GP
        t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)
        t_obs = np.ravel(t_obs)
        y_obs = np.ravel(y_obs)
        err_obs = np.ravel(err_obs)

        # Preparo GP, l son 6 dias segun lo observado en otros papers
        var = np.var(y_obs)
        l = 6 * (max_time - min_time) / float(total_days)
        kernel = var ** 2 * kernels.ExpSquaredKernel(l ** 2)

        gp = george.GP(kernel, mean=np.mean(y_obs))
        gp.compute(t_obs, yerr=err_obs)

        # Sampleo curvas del GP
        samples = []
        x = np.linspace(min_time, max_time, n_points)

        samples = gp.sample_conditional(y_obs, t_obs, n_samples)
        deviations = map(lambda s: np.sqrt(np.diag(gp.predict(s, x)[1])),
                         samples)

        samples_devs = zip(samples, deviations)
        samples_devs = (t_obs, samples_devs)

        result_dir = (MODULE_PATH + 'GP Samples/' + str(int(100 * percentage)) +
                      '%/' + lu.get_lc_class_name(lc_path) + '/' +
                      lu.get_lightcurve_id(lc_path) + ' samples.pkl')

        output = open(result_dir, 'wb')
        pickle.dump(samples_devs, output)
        output.close()

    except Exception as e:
        print e

def test(lc_path, percentage=1.0):
    
    lc = lu.open_lightcurve(lc_path)
    print int(percentage * lc.index.size)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    total_days = lc.index[-1] - lc.index[0]
    n_points = lc.index.size

    # Preparo la curva para alimentar el GP
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)
    t_obs = np.ravel(t_obs)
    y_obs = np.ravel(y_obs)
    err_obs = np.ravel(err_obs)

    var = np.var(y_obs)
    l = 6 * (max_time - min_time) / float(total_days)
    kernel = var ** 2 * kernels.ExpSquaredKernel(l ** 2)

    gp = george.GP(kernel, mean=np.mean(y_obs))
    
    if not gp.computed:
        gp.compute(t_obs, yerr=err_obs)
    
    return lc


