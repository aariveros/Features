# coding=utf-8

# Varios métodos útiles para el manejo de curvas de luz

# -----------------------------------------------------------------------------

from __future__ import division
import numpy as np
import pandas as pd
import re

from config import *

import random

def has_both_bands(lc_path, allpaths=LC_FILE_PATH):
    """
    lc_path: path de una curva
    all_paths: path de el archivo la direccion de las curvas
    """
    
    if not 'B.mjd' in lc_path:
        return False
    
    red = lc_path.replace('B.mjd', 'R.mjd')
    
    if not red in all_paths:
        return False
    return True


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

    return t_obs, y_obs, err_obs, min_time, max_time


def open_lightcurve(fp):
    """
    fp: Absolute file path of the lightcurve file
    """
    cols = ['mjd', 'mag', 'err']
    data = pd.read_table(fp, skiprows = [0,1,2], names = cols,
            index_col = 'mjd', sep = '\s+')
    return data


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

    [magnitud_media, error_medio] = lc.mean(axis = 0)

    lc = lc[(lc['err'] < rango * error_medio) & (np.abs(lc['mag'] - magnitud_media) / lc['mag'].std() < 5 )]

    # lc = lc[lc['err'] < rango * error_medio]

    if norm:
        pass

    return lc