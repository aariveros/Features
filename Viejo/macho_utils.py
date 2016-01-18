# coding=utf-8

# Varios métodos útiles para el manejo de curvas de luz

# -----------------------------------------------------------------------------

from __future__ import division
import pandas as pd
import re

from config import *


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