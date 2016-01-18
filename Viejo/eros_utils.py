# coding=utf-8

# Métodos útiles para el manéjo de curvas de EROS
# -----------------------------------------------------------------------------

import numpy as np
import pandas as pd

import re

from config import *

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

    # Filtros para las observaciones cuya magnitud o error esta equivocada
    a = lambda x: not np.isclose(x, 99.999)
    b = lambda x: not np.isclose(x, 9.999)

    data = data[ (data['mag'].apply(a)) | (data['err'].apply(b)) ]
    return data