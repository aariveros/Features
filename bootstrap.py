# coding=utf-8

# Métodos para el desarrollo de bootstraping en series de tiempo
# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
# import lightcurves.eros_utils as lu

from config import *

import random
import cPickle

from george import kernels
import numpy as np
import george
import FATS
import pandas as pd

import matplotlib.pyplot as plt

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

def GP_complete_lc(lc, total_points):
    """Recibe una curva de luz, le ajusta un modelo de GP y utilizando el valor
    medio de este, agrega nuevas observaciones separadas homogeneamente
    a las observaciones reales

    PODRIA AGREGAR EL LENGTH SCALE DEL GAUSSIAN PROCESS (NUMERO DE DIAS)

    lc: curva de luz a completar
    total_points: Numero total de observaciones que se desea alcanzar

    return: curva con observaciones agregadas
    """
    
    total_days = lc.index[-1] - lc.index[0]
    n_points = lc.index.size

    if total_points <= n_points:
        return lc

    # Agrego 2 puntos pq siempre hay que descartar el primero y el ultimo
    # que topan con los de la curva original
    missing_points = total_points - n_points + 2

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

    # Sampleo uniformemente la cantidad de observaciones que me faltan
    x = np.linspace(min_time, max_time, missing_points)
    mu, cov = gp.predict(y_obs, x)

    new_y = mu * lc['mag'].std() + lc['mag'].mean()
    new_y = new_y[1:-1]

    # Tengo que desnormalizar las posiciones que entrega el GP
    observed_days = np.array(lc.index).reshape(len(lc.index),1)
    new_t = x * np.std(observed_days) + np.mean(observed_days)
    new_t = new_t[1:-1]

    new_err = np.sqrt(np.diag(cov))[1:-1]
    new_err = new_err * lc['mag'].std()

    lc_2 = pd.DataFrame({'mag':new_y, 'err': new_err}, index=new_t)

    return pd.concat([lc, lc_2]).sort_index()

def GP_sample_mean(lc_path, result_dir='', percentage=1.0):
    """Recibe una curva ajusta un GP (sobreajustado) y guarda las medias del
    modelo

    lc_path: path de la curva de luz
    percentage: porcentaje de la curva a utilizar
    """
    try:
        print lc_path
        lc = lu.open_lightcurve(lc_path)
        lc = lu.filter_data(lc)
        lc = lc.iloc[0:int(percentage * lc.index.size)]

        total_days = lc.index[-1] - lc.index[0]

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

        mu, cov = gp.predict(y_obs, t_obs)
        sigma = np.sqrt(np.diag(cov))

        fitted_curve = (t_obs, mu, sigma)

        result_path = (result_dir + lu.get_lc_class_name(lc_path) + '/' +
                      lu.get_lightcurve_id(lc_path) + '.pkl')

        output = open(result_path, 'wb')
        cPickle.dump(fitted_curve, output)
        output.close()

    except Exception as e:
        print e
        err_path = result_dir + 'error.txt'
        f = open(err_path, 'a')
        f.write(lc_path + '\n')
        f.close()

def GP_bootstrap(lc_path, percentage=1.0, n_samples=100):
    """Recibe una curva hace un sampleo con un GP sobreajustado
    y retorna las muestras obtenidas

    lc_path: path de la curva de luz
    percentage: porcentaje de la curva a utilizar
    """
    
    lc = lu.open_lightcurve(lc_path)
    lc = lu.filter_data(lc)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    total_days = lc.index[-1] - lc.index[0]

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

    samples = gp.sample_conditional(y_obs, t_obs, n_samples)

    deviations = map(lambda s: np.sqrt(np.diag(gp.predict(y_obs, t_obs)[1])),
                     samples)

    samples_devs = zip(samples, deviations)
    samples_devs = (t_obs, samples_devs)

    return samples_devs

def graf_GP(lc_path, percentage=1.0):

    lc = lu.open_lightcurve(lc_path)
    lc = lu.filter_data(lc)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    total_days = lc.index[-1] - lc.index[0]

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

    x = np.linspace(np.min(t_obs), np.max(t_obs), 500)
    mu, cov = gp.predict(y_obs, x)
    std = np.sqrt(np.diag(cov))

    plt.figure()

    plt.plot(x, mu, color="#4682b4", alpha=0.3)
    plt.errorbar(t_obs, y_obs, yerr=err_obs, fmt=".b", ecolor='r', capsize=0)

    # Agrego el intervalo de confianza
    plt.fill(np.concatenate([x, x[::-1]]), \
            np.concatenate([mu - 1.9600 * std,
                           (mu + 1.9600 * std)[::-1]]), \
            alpha=.5, fc='#C0C0C0', ec='None', label='95% confidence interval')

    plt.show()
    plt.close()


def parallel_bootstrap(lc_path, percentage=1.0, n_samples=100):
    """Recibe una curva hace un sampleo con un GP sobreajustado
    y guarda las muestras obtenidas

    lc_path: path de la curva de luz
    percentage: porcentaje de la curva a utilizar
    """
    try:
        print lc_path
        lc = lu.open_lightcurve(lc_path)
        lc = lu.filter_data(lc)
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

        # ESTO ESTA RARO!!! S NO SE OCUPA, POR LO QUE TODAS LAS DESVIACIONES
        # SON LAS MISMAS. ESTA ESO BIEN???
        # ADEMAS NO ESTOY PIDIENDO LAS DESVIACIONES EN EL MISMO LUGAR DDE
        # SAQUE LAS MUESTRAS. ESO SI O SI ESTA MAL
        deviations = map(lambda s: np.sqrt(np.diag(gp.predict(y_obs, x)[1])),
                         samples)

        samples_devs = zip(samples, deviations)
        samples_devs = (t_obs, samples_devs)

        # result_dir = (LAB_PATH + 'GP_Samples/MACHO/' + str(int(100 * percentage)) +
        #               '%/' + lu.get_lc_class_name(lc_path) + '/' +
        #               lu.get_lightcurve_id(lc_path) + ' samples.pkl')
        
        result_dir = (LAB_PATH + 'GP_Samples/EROS/' + str(int(100 * percentage)) +
                      '%/' + lu.get_lc_class_name(lc_path) + '/' +
                      lu.get_lightcurve_id(lc_path) + ' samples.pkl')

        output = open(result_dir, 'wb')
        cPickle.dump(samples_devs, output)
        output.close()

    except Exception as e:
        print e
        err_path = LAB_PATH + 'GP_Samples/MACHO/' + str(int(100 * percentage)) + '%/error.txt'
        f = open(err_path, 'a')
        f.write(lc_path + '\n')
        f.close()

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
