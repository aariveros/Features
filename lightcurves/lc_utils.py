# coding=utf-8

# Métodos para el manejo de curvas de luz de distintos catalogos
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np

import random
import os
import re

from config import *

def filter_data(lc, rango=3):
    """Recibe una curva de luz, y la retorna eliminando todos los puntos
    que se encuentran fuera de una cantidad errores promedio

    Parameters
    ----------

    lc: dataframe de la curva de luz
    rango: rango de filtro, default 3 medias del error
    """

    [magnitud_media, error_medio] = lc.mean(axis = 0)
    lc = lc[(lc['err'] < rango * error_medio) & (np.abs(lc['mag'] - magnitud_media) / lc['mag'].std() < 5 )]

    return lc

def get_ids_in_path(directory, catalog='MACHO', extension=''):
    """Busca todos los csv de un directorio, encuentra los ids y los retorna
    """
    ids = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if extension in f:
                ids.append(get_lightcurve_id(os.path.abspath(os.path.join(dirpath, f))))
    return ids

def get_lightcurve_band(fp):
    """Método solo para las curvas de MACHO

    fp: lightcurve file path
    return val: band as a string
    """
    if ".R.mjd" in fp:
        return "R"
    elif ".B.mjd" in fp:
        return "B"

def get_lightcurve_class(fp, catalog='MACHO'):
    """
    Para eros estoy asumiendo que las curvas están separadas en directorios por
    clase. Y que el path que estoy pasando es el de la curva
    """
    
    if catalog == 'MACHO':
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

    elif catalog == 'EROS':
        return fp.split('/')[-2]

def get_lightcurve_id(fp, catalog='MACHO'):
    """
    return val: string containing de macho_id of the curve
    """

    if catalog == 'MACHO':
        pattern = re.compile('[0-9]*\.[0-9]*\.[0-9]*')
        return pattern.search(fp).group()

    elif catalog == 'EROS':
        pattern = re.compile('lm[^. ]*')
        return pattern.search(path).group()

    elif catalog == 'OGLE':
        pass

def get_lightcurve_paths(path=LC_FILE_PATH, separate_bands=False, catalog='MACHO'):
    """
    return val: file object with lightcurve paths in each line
    """
    f = open(path, 'r')
    
    if catalog == 'MACHO':
        
        if separate_bands:
            azules = [l[:-1] for l in f if '.B.mjd' in l]
            f.seek(0)
            rojas = [l[:-1] for l in f if '.R.mjd' in l]
            return azules, rojas
        else:   
            return [l[:-1] for l in f]
    
    elif catalog == 'EROS':
        return [line[:-1] for line in f if '.time' in line]

    elif catalog == 'OGLE':
        pass

def get_paths(directory, extension=''):
    """Entrega todos los paths absolutos a objetos de distintos tipos en un
    directorio
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if extension in f:
                yield(os.path.abspath(os.path.join(dirpath, f)))

def has_both_bands(lc_path, allpaths=LC_FILE_PATH):
    """Metodo para la curvas de MACHO
    lc_path: path de una curva
    all_paths: path de el archivo la direccion de las curvas
    """
    
    if not 'B.mjd' in lc_path:
        return False
    
    red = lc_path.replace('B.mjd', 'R.mjd')
    
    if not red in all_paths:
        return False
    return True

def open_lightcurve(fp, catalog='MACHO'):
    """
    fp: Absolute file path of the lightcurve file
    """
    if catalog == 'MACHO':
        cols = ['mjd', 'mag', 'err']
        data = pd.read_table(fp, skiprows = [0,1,2], names = cols,
                index_col = 'mjd', sep = '\s+')
        return data

    elif catalog == 'EROS':
        cols = ['mjd', 'mag', 'err', 'magB', 'errB']
        data = pd.read_csv(fp, skiprows=4, names=cols, index_col='mjd',
                           sep='\s+', engine='python')
        data = data[['mag', 'err']]

        # Filtros para las observaciones cuya magnitud o error esta equivocada
        a = lambda x: not np.isclose(x, 99.999)
        b = lambda x: not np.isclose(x, 9.999)

        data = data[ (data['mag'].apply(a)) | (data['err'].apply(b)) ]
        return data


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

    t_obs = np.ravel(t_obs)
    y_obs = np.ravel(y_obs)
    err_obs = np.ravel(err_obs)

    return t_obs, y_obs, err_obs, min_time, max_time
