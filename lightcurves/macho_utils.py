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