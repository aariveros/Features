# coding=utf-8

# Métodos para el desarrollo de bootstraping en series de tiempo
# -----------------------------------------------------------------------------

import random
import cPickle

import george
import numpy as np
import pandas as pd
from george import kernels

import optimize
from config import *
import lightcurves.lc_utils as lu


def prepare_GP():
    pass

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

def GP_sample_mean(lc_path, catalog='MACHO', percentage=1.0, sampling='equal',
                   param_choice='fitted', result_dir=''):
    """Recibe una curva ajusta un GP y guarda las medias del
    modelo
    """

    try:
        lc = lu.open_lightcurve(lc_path, catalog=catalog)
        lc = lu.filter_data(lc)
        lc = lc.iloc[0:int(percentage * lc.index.size)]

        t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

        # Preparo GP, l son 6 dias segun lo observado en otros papers
        var = np.var(y_obs)
        l = 6
        kernel = var * kernels.ExpSquaredKernel(l ** 2)

        if param_choice == 'fitted':
            kernel = optimize.find_best_fit(kernel, t_obs, y_obs, err_obs)
            kernel = kernel + kernels.WhiteKernel(np.var(err_obs))

        gp = george.GP(kernel, mean=np.mean(y_obs))
        gp.compute(t_obs, yerr=err_obs)

        if sampling == 'uniform':
            x = np.linspace(min_time, max_time, len(t_obs))
            mu, cov = gp.predict(y_obs, x)
        else:
            mu, cov = gp.predict(y_obs, t_obs)
        
        sigma = np.sqrt(np.diag(cov))
        fitted_curve = (t_obs, mu, sigma)
        result_path = (result_dir +
                       lu.get_lightcurve_class(lc_path, catalog=catalog) +
                       '/' + lu.get_lightcurve_id(lc_path, catalog=catalog) +
                       '.pkl')

        output = open(result_path, 'wb')
        cPickle.dump(fitted_curve, output)
        output.close()

    except Exception as e:
        print e
        err_path = result_dir + 'error.txt'
        f = open(err_path, 'a')
        f.write(lc_path + '\n')
        f.close()

def GP_bootstrap(lc, kernel, sampling='equal', n_samples=100):
    """Recibe una curva hace un sampleo con un GP sobreajustado
    y retorna las muestras obtenidas

    lc: curva de luz a samplear
    kernel: kernel de george a utilizar
    sampling:   uniform - las curvas sampleadas se toman a intervalos uniformes
                equal - las curvas se toman en los mismos instantes que la
                        curva original
    n_samples: number of samples taken
    """

    # Preparo la curva para alimentar el GP
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

    gp = george.GP(kernel, mean=np.mean(y_obs))
    gp.compute(t_obs, yerr=err_obs)

    if sampling == 'uniform':
        x = np.linspace(min_time, max_time, len(t_obs))
        samples = gp.sample_conditional(y_obs, x, n_samples)
    else:
        samples = gp.sample_conditional(y_obs, t_obs, n_samples)

    # Esto no es necesario. Todos los errores son iguales
    deviations = map(lambda s: np.sqrt(np.diag(gp.predict(y_obs, t_obs)[1])),
                     samples)

    samples_devs = zip(samples, deviations)
    samples_devs = (t_obs, samples_devs)

    return samples_devs


def parallel_bootstrap(lc_path, kernel, sampling, percentage=1.0, n_samples=100, catalog='MACHO'):
    """Recibe una curva hace un sampleo con un GP sobreajustado
    y guarda las muestras obtenidas

    lc_path: path de la curva de luz
    percentage: porcentaje de la curva a utilizar
    """
    try:
        print lc_path
        lc = lu.open_lightcurve(lc_path, catalog=catalog)
        lc = lu.filter_data(lc)
        lc = lc.iloc[0:int(percentage * lc.index.size)]

        total_days = lc.index[-1] - lc.index[0]
        n_points = lc.index.size

        # Preparo la curva para alimentar el GP
        t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

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

        deviations = map(lambda s: np.sqrt(np.diag(gp.predict(y_obs, x)[1])),
                         samples)

        samples_devs = zip(samples, deviations)
        samples_devs = (t_obs, samples_devs)
        
        result_dir = (LAB_PATH + 'GP_Samples/' + catalog + '/' +
                      str(int(100 * percentage)) + '%/' + 
                      lu.get_lightcurve_class(lc_path, catalog=catalog) + '/' +
                      lu.get_lightcurve_id(lc_path, catalog=catalog) +
                      ' samples.pkl')

        output = open(result_dir, 'wb')
        cPickle.dump(samples_devs, output)
        output.close()

    except Exception as e:
        print e
        err_path = LAB_PATH + 'GP_Samples/' + catalog + '/' + str(int(100 * percentage)) + '%/error.txt'
        f = open(err_path, 'a')
        f.write(lc_path + '\n')
        f.close()

def test(lc_path, percentage=1.0, catalog='MACHO'):
    
    lc = lu.open_lightcurve(lc_path, catalog=catalog)
    print int(percentage * lc.index.size)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    total_days = lc.index[-1] - lc.index[0]
    n_points = lc.index.size

    # Preparo la curva para alimentar el GP
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

    var = np.var(y_obs)
    l = 6 * (max_time - min_time) / float(total_days)
    kernel = var ** 2 * kernels.ExpSquaredKernel(l ** 2)

    gp = george.GP(kernel, mean=np.mean(y_obs))
    
    if not gp.computed:
        gp.compute(t_obs, yerr=err_obs)
    
    return lc
