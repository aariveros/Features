from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

import sys

from config import *

import random

def prepare_lightcurve(curva, n_sampled_points):
    """Toma una curva y la procesa para poder ocuparla en un GP.

    parameters
    ----------
    curva: pandas dataframe -> [index: mjd][col: mag]
    n_sampled_points: cantidad de puntos de la curva que se van a ocupar
    """
    t_obs = np.array(curva.index.reshape(len(curva.index),1))
    t_obs = (t_obs - np.mean(t_obs)) / np.std(t_obs)

    # Array con los brillos normalizados
    y_obs = curva['mag'].reshape(len(curva.index), 1)
    y_obs = (y_obs - np.mean(y_obs)) / np.std(y_obs)

    # Array con los errores de las mediciones normalizados segun las observaciones
    # No tiene sentido centrar los errores
    err_obs = curva['err'].reshape(len(curva.index), 1)
    err_obs = err_obs / curva['mag'].std()

    min_time = np.min(t_obs)
    max_time = np.max(t_obs)

    # Tomo una muestra aleatoria de puntos de la curva de luz (como?)
    random.seed(1)
    rand_indices = random.sample(range(0,np.max(np.shape(t_obs))),n_sampled_points)
    rand_indices.sort()

    t_obs = t_obs[rand_indices]
    y_obs = y_obs[rand_indices]
    err_obs = err_obs[rand_indices]

    # Transformo a matriz
    t_obs = np.asmatrix(t_obs)
    y_obs = np.asmatrix(y_obs)
    err_obs = np.asmatrix(err_obs)

    return t_obs, y_obs, err_obs, min_time, max_time

def graf_gp_fit(X, y, x_pred, y_pred, sigma):
    """Graf an adjusted gaussian process model over a set of points.
    
    parameters
    ----------
    X: puntos de las observaciones
    y: valor de f(x) en las observaciones
    x_pred: puntos donde se pregunta al gp
    y_pred: f(x) dde se pregunto al gp
    sigma: std en los ptos dde se pregunto al modelo
    
    """
    # Grafico las observaciones
    X2 = np.array(X)
    X2 = (X2.T).ravel()
    plt.plot(X2,y,'.r')
    
    # Grafico la regresion ajustada
    X3 = np.array(x_pred)
    X3 = X3.ravel()
    plt.plot(X3, y_pred, 'b-', label=u'Prediction')
    
    # Agrego el intervalo de confianza
    plt.fill(np.concatenate([X3, X3[::-1]]), \
            np.concatenate([y_pred - 1.9600 * sigma,
                           (y_pred + 1.9600 * sigma)[::-1]]), \
            alpha=.5, fc='#C0C0C0', ec='None', label='95% confidence interval')
    
    # Leyenda
    plt.xlabel('$x$')
    plt.ylabel('$f(x)$')
    plt.legend(loc='upper right')


def open_lightcurve(fp):
    """
    fp: Absolute file path of the lightcurve file
    """
    cols = ['mjd', 'mag', 'err']
    data = pd.read_table(fp, skiprows = [0,1,2], names = cols,
            index_col = 'mjd', sep = '\s+')
    return data

def open_lightcurves(lc_list):
    """
    lc_list: iterable with lightcurve file paths
    returns: list with Pandas DataFrames for each lightcurve
    """
    return map(open_lightcurve, lc_list)


def get_lightcurve_paths(path=LC_FILE_PATH, separate_bands=False):
    """
    return val: file object with lightcurve paths in each line
    """
    f = open(path, 'r')

    if separate_bands:
        azules = [l[:-1] for l in f if '.B.mjd' in l]
        f.seek(0)
        rojas = [l[:-1] for l in f if '.R.mjd' in l]
        return azules, rojas
    else:   
        return [l[:-1] for l in f]


def get_lightcurve_id(fp):
    """
    return val: string containing de macho_id of the curve
    """
    pattern = re.compile('[0-9]*\.[0-9]*\.[0-9]*')
    return pattern.search(fp).group()

def get_lc_class(fp):
    """
    fp: lightcurve file path
    return val: class as an integer
    """
    if "Be_lc" in fp:
        return 2
    elif "CEPH" in fp:
        return 3
    elif "EB" in fp:
        return 4
    elif "longperiod_lc" in fp:
        return 5
    elif "microlensing_lc" in fp:
        return 6
    elif "non_variables" in fp:
        return 7
    elif "quasar_lc" in fp:
        return 8
    elif "RRL" in fp:
        return 9
    return 0

def get_lc_class_name(fp):
    if "Be_lc" in fp:
        return "Be_lc"
    elif "CEPH" in fp:
        return "CEPH"
    elif "EB" in fp:
        return "EB"
    elif "longperiod_lc" in fp:
        return "longperiod_lc"
    elif "microlensing_lc" in fp:
        return "microlensing_lc"
    elif "non_variables" in fp:
        return "non_variables"
    elif "quasar_lc" in fp:
        return "quasar_lc"
    elif "RRL" in fp:
        return "RRL"
    else:
        return '0'    


def get_lc_name(fp):
    """
     Retorna el nombre de la clase de la estrella
    """
    # /Users/npcastro/Dropbox/Tesis/lightcurves/Be_lc/lc_1.3567.1310.B.mjd
    pattern = re.compile('lightcurves/.*/')
    return pattern.search(fp).group().split('/')[1]

def get_lc_band(fp):
    """
    fp: lightcurve file path
    return val: band as a string
    """
    if ".R.mjd" in fp:
        return "R"
    elif ".B.mjd" in fp:
        return "B"



def filter_data( lc, rango = 3, norm = False ):
    """ Recibe una curva de luz, y la retorna eliminando todos los puntos
     que se encuentran fuera de una cantidad errores promedio

     Parameters
     ----------

     lc: dataframe de la curva de luz
     rango: rango de filtro, default 3 medias del error
     norm: si es true la curva se centra en 0, default false
    """

    [magnitud_media, error_medio] = lc.mean( axis = 0)

    lc = lc[lc['err'] < rango * error_medio]

    if norm:
        pass

    return lc

def feature_progress( lc, feature, percentage=1 ):
    """
     Retorna el valor de una feature calculada con la curva cortada hasta distintos
     porcentajes. Y el porcentaje de completitud de la curva.

     percentage: si se especifica un porcentaje, ese porcentaje de veces se calcula 
     la feature 
    """
    x_values = []
    y_values = []

    steps = int(len(lc.index) / percentage) - 2

    for i in range(3, steps):
        y_values.append(feature( lc.iloc[0:i*percentage]) )
        
        aux = float(i*percentage)/len(lc.index)
        # x_values.append( aux )

        # print('Progress: ' + '{0:.2f}'.format(aux*100) + '%')    
        sys.stdout.write('Progress: ' + '{0:.2f}'.format(aux*100) + '%')
        sys.stdout.flush()

        x_values.append(i*percentage)

    x_values.append(len(lc.index))
    y_values.append(feature(lc))

    return x_values, y_values


def get_feat_and_comp(lc, feature, comp, percentage=1):
    """Retorna los valores de una feature calculada progresivamente a medida que se completa
    la curva. Ademas retorna la confianza en la feature a medida que esta avanza

    parameters
    ----------

    percentage:    Fraccion de puntos de la curva para los que se calculara la feature. Sirve
                   para acelerar el calculo de features mas lentas. 

    """
    x_values, y_values = feature_progress(lc, feature, percentage)
    
    completitud = []
    for i in range(2, len(y_values)):
        completitud.append(comp(y_values[0:i]))

    return x_values, y_values, completitud

def completeness( y_values ):
    """Retorna el grado de confianza de una feature incompleta.
    Retorna 1 -  el promedio de las diferencias entre cada punto y
    el antecesor. Considera max_var como la maxima diferencia presente, 
    entre un punto y el siguiente (en valor absoluto) en la curva de luz. 
    """
    variaciones = []
    n = len(y_values)

    for i in range(1, n):
        variaciones.append(abs(y_values[i] - y_values[i-1]))

    max_var = max(variaciones)
    min_var = 0
    # min_var = min(variaciones)

    prom_var = sum(variaciones) / (n - 1)

    # print( 'Maxima varianza: ' + str(max_var))
    # print( 'Minima varianza: ' + str(min_var))
    # print( 'Promedio de varianza. ' + str(aux))
    return prom_var
    #return 1 - normalize( prom_var, min_var, max_var)

def var_completeness( y_values ):
    """Retorna el grado de confianza de una feature incompleta.   
    Retorna 1 - la varianza de los datos, normalizada entre 0 y max_var.
    Considera max_var como la maxima diferencia con la media de los datos.
    """

    n = len(y_values)
    media = np.mean( y_values )
    variaciones = []

    max_var = 0
    min_var = 0

    for i in range(len(y_values)):
        aux = (y_values[i] - media)**2

        if( aux > max_var):
            max_var = aux

        variaciones.append(aux)

    varianza = sum(variaciones) / (n-1)
    
    return varianza
    #return 1 - normalize( varianza, min_var, max_var)

def trust( y_values ):
    """Calcula la confianza de una feature incompleta. 
    Retorna 1 - el promedio de las diferencias entre cada punto y
    el ultimo valor de la feature. Considera max_var como la maxima diferencia presente, 
    entre un punto y el ultimo valor de la feature en la curva de luz.

    """
    n = len(y_values)
    final = y_values[-1]

    variaciones = []
    max_var = 0
    min_var = 0

    for i in range(len(y_values)):
        aux = abs(y_values[i] - final)

        if(aux > max_var):
            max_var = aux
        variaciones.append(aux)

    prom_var = sum(variaciones) / (n - 1)

    return prom_var
    #return 1 - normalize(prom_var, min_var, max_var)

def completition_progress( y_values ):
    """Retorna el grado de completitud de una feature para cada cantidad de puntos 
    posibles
    """
    pass


def normalize( d, minimo, maximo, new_min=0, new_max=1 ):
    if(maximo == minimo):
        return d * (new_max - new_min) + new_min
    else:
        return (float(d - minimo) / (maximo - minimo)) * (new_max - new_min) + new_min
