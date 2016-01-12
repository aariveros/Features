# coding=utf-8
# Archivo con métodos generales que ocupo repetidamente en mi codigo

# -----------------------------------------------------------------------------

import numpy as np
import random

import os

def get_paths(directory, extension=''):
    """Entrega todos los paths absolutos a objetos de distintos tipos en un
    directorio
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if extension in f:
               	yield(os.path.abspath(os.path.join(dirpath, f)))


def prepare_lightcurve(curva, n_sampled_points=None):
    """Toma una curva y la procesa para poder ocuparla en un GP.
        

    Parameters
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

    return t_obs, y_obs, err_obs, min_time, max_time