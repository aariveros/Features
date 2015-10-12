# coding=utf-8

# Métodos útiles para el manéjo de curvas de EROS
# -----------------------------------------------------------------------------

import numpy as np
import pandas as pd

import random
import re

from config import *

def filter_data( lc, rango=3, norm=False ):
    """ Recibe una curva de luz, y la retorna eliminando todos los puntos
     que se encuentran fuera de una cantidad errores promedio

     Parameters
     ----------

     lc: dataframe de la curva de luz
     rango: rango de filtro, default 3 medias del error
     norm: si es true la curva se centra en 0, default false
    """

    [magnitud_media, error_medio] = lc.mean(axis = 0)

    lc = lc[(lc['err'] < rango * error_medio) & (np.abs(lc['mag'] - magnitud_media) / lc['mag'].std() < 5 )]

    return lc

def get_lc_class_name(fp):

    return fp.split('/')[-2]

def get_lightcurve_id(path):
    """Recibe un path absoluto a un archivo de una curva de luz de EROS y 
    retorna el id de la curva
    """
    pattern = re.compile('lm[^. ]*')
    return pattern.search(path).group()

def get_lightcurve_paths(path=EROS_FILE_PATH):
    """
    EROS_FILES_PATH: file with the absolutes paths of the lightcurves in each line

    returns val: file object with lightcurve paths in each line
    """
    f = open(path, 'r')
    return [line[:-1] for line in f if '.time' in line]

def open_lightcurve(fp):
    """
    fp: absolute file path of the lightcurve
    TODO: definir bien como se va a manejar curvas con dos tipos de bandas
    """
    cols = ['mjd', 'mag', 'err', 'magB', 'errB']
    data = pd.read_csv(fp, skiprows=4, names=cols, index_col='mjd',
                       sep='\s+', engine='python')
    data = data[['mag', 'err']]
    return data


def prepare_lightcurve(curva, n_sampled_points=None):
    """Toma una curva y la procesa para poder ocuparla en un GP.

    parameters
    ----------
    curva: pandas dataframe -> [index: mjd][col: mag, err]
    n_sampled_points: cantidad de puntos de la curva que se van a ocupar
    """

    # Es necesario normalizar las observaciones y los tiempos?
    t_obs = np.array(curva.index).reshape(len(curva.index),1)
    t_obs = (t_obs - np.mean(t_obs)) / np.std(t_obs)

    y_obs = curva['mag'].reshape(len(curva.index), 1)
    y_obs = (y_obs - np.mean(y_obs)) / np.std(y_obs)

    # Array con los errores de las mediciones normalizados segun las observaciones
    # No tiene sentido centrar los errores
    # Pero hay que normalizarlos igual que a la magnitud
    err_obs = curva['err'].reshape(len(curva.index), 1)
    err_obs = err_obs / curva['mag'].std()

    min_time = np.min(t_obs)
    max_time = np.max(t_obs)

    # Tomo una muestra aleatoria de puntos de la curva de luz (como?)
    if not (n_sampled_points is None):
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
