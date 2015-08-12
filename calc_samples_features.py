# coding=utf-8

# Toma un directorio con muestras sampleadas de curvas de luz y para cada 
# una calcula un set de Features, y guarda un dataframe con los valores en
# algun directorio

# --------------------------------------------------------------------------

import lightcurves.lc_utils as lu
from config import *
import bootstrap

from functools import partial
import multiprocessing
import pickle
import sys
import os

import pandas as pd
import FATS


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

    # Puedo especificar las featurs a ocupar o las features a excluir.
    # Depende que sea mas simple
    # feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
    #                 'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
    #                 'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'PercentDifferenceFluxPercentile',
    #                 'Q31', 'Rcs', 'Skew', 'SlottedA_length', 'SmallKurtosis',
    #                 'Std', 'StetsonK','StetsonK_AC']
    # exclude_list = []
    
    feature_list = []
    exclude_list = ['Color', 'Eta_color', 'Q31_color', 'StetsonJ', 'StetsonL',
                    'CAR_mean', 'CAR_sigma', 'CAR_tau']

    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)

    feat_names = fs.featureList
    print feat_names
    del fs

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

        partial_calc = partial(bootstrap.calc_features, t_obs,
                               feature_list=feature_list,
                               exclude_list=exclude_list)
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

            df = pd.DataFrame(feature_values, columns=feat_names)
            df.to_csv(file_path, index=False)

        if count >= 20:
            break
        count += 1
        
