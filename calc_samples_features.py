# coding=utf-8

# Toma un directorio con muestras sampleadas de curvas de luz y para cada 
# una calcula un set de Features, y guarda un dataframe con los valores en
# algun directorio

# --------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd

import multiprocessing
import sys
import pickle
import re
import os

import FATS

from config import *

def get_paths(directory):
    """Entrega todos los paths absolutos a objetos serializados de un directorio
    """
    files = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                files.append(os.path.abspath(os.path.join(dirpath, f)))
    return files

def calc_features(samples_path):
    feature_values = []
    
    # Elimino features que involucran color y las CAR por temas de tiempo
    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], featureList=None,
                           excludeList=['Color', 'Eta_color', 'Q31_color',
                           'StetsonJ','StetsonL', 'CAR_mean', 'CAR_sigma', 'CAR_tau'])
    
    # Las muestras vienen en una tupla s[0] es los tiempos de medicion
    # s[1] es un arreglo para cada muestra donde cada muestra tiene dos
    # arreglos uno para las observaciones y otro para los errores
    f = open(samples_path, 'r')
    samples = pickle.load(f)
    f.close()
    
    # Estas variables son comunes a todas las muestras
    t_obs = samples[0]
    lc_class = lu.get_lc_class_name(samples_path)
    macho_id = lu.get_lightcurve_id(samples_path)

    # Viene con el porcentaje ej: 15%
    pattern = re.compile('[0-9]*\%')
    percentage = pattern.search(samples_path).group()

    for s in samples[1]:
        y_obs = s[0]
        err_obs = s[1]

        fs = fs.calculateFeature([y_obs, t_obs, err_obs])
        feature_values.append(map(lambda x: float("{0:.6f}".format(x)),
                                  fs.result(method='dict').values()))

    # Escribo los resultados en un archivo especial para cada curva original
    file_path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '/' + lc_class + '/' + macho_id + '.csv'

    df = pd.DataFrame(feature_values, columns = fs.featureList())
    df.to_csv(file_path, index=False)

if __name__ == '__main__':

    if len(sys.argv) == 3:
        percentage = sys.argv[1]
        n_jobs = int(sys.argv[2])
    elif len(sys.argv) == 2:
        percentage = sys.argv[1]
        n_jobs = 30
    else:
        percentage = '100'
        n_jobs = 30

    path = LAB_PATH + 'GP_Samples/MACHO/' + percentage + '%/'

    # Obtengo los archivos con las muestras serializadas
    files = get_paths(path)

    chunksize = int(len(files)/n_jobs)
    pool = multiprocessing.Pool(processes=n_jobs)
    pool.map(calc_features, files, chunksize)
