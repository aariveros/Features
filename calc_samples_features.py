# coding=utf-8

# Toma un directorio con muestras sampleadas de curvas de luz y para cada 
# una calcula un set de Features, y guarda un dataframe con los valores en
# algun directorio

# --------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import sys
import multiprocessing
import FATS
import os
from functools import partial
from config import *
import re
import pandas as pd
import pickle

import bootstrap

def get_paths(directory):
    """Entrega todos los paths absolutos a objetos serializados de un directorio
    """

    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                yield(os.path.abspath(os.path.join(dirpath, f)))


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
    feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
                    'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
                    'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'PercentDifferenceFluxPercentile',
                    'Q31', 'Rcs', 'Skew', 'SlottedA_length', 'SmallKurtosis',
                    'Std', 'StetsonK','StetsonK_AC']
    count = 0
    for f in files:
 
        # Las muestras vienen en una tupla, s[0] es una lista con los tiempos de medicion
        # s[1] es una lista de  muestras  donde cada muestra tiene dos
        # arreglos uno para las observaciones y otro para los errores
        aux = open(f, 'r')
        samples = pickle.load(aux)
        aux.close()

        # Estas variables son comunes a todas las muestras
        t_obs = samples[0]
        lc_class = lu.get_lc_class_name(f)
        macho_id = lu.get_lightcurve_id(f)

        # partial_calc = partial(bootstrap.calc_features, t_obs, fs)
        partial_calc = partial(bootstrap.calc_features, t_obs)
        error = False
        chunksize = int(100/n_jobs)

        try:
            pool = multiprocessing.Pool(processes=n_jobs)
            feature_values = pool.map(partial_calc, samples[1], chunksize)

            pool.close()
            pool.join()

        except Exception as e:
            error = True
            raise

        if error:
            aux = open(LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%/errores.txt', 'a')
            aux.write(f + '\n')
            aux.close()
        else:
            # Escribo los resultados en un archivo especial para cada curva original
            file_path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%/' + lc_class + '/' + macho_id + '.csv'

            df = pd.DataFrame(feature_values, columns=feature_list)
            df.to_csv(file_path, index=False)

        if count >= 200:
            break
        count += 1
        
