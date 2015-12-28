# coding=utf-8

# Toma un directorio con muestras sampleadas de curvas de luz y para cada 
# una calcula un set de Features, y guarda un dataframe con los valores en
# algun directorio

# --------------------------------------------------------------------------

import lightcurves.eros_utils as lu
from config import *
import parallel

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

def get_ids_in_paths(directory):
    """Busca todos los csv de un directorio, encuentra los ids y los retorna
    """
    ids = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.csv' in f:
                ids.append(lu.get_lightcurve_id(os.path.abspath(os.path.join(dirpath, f))))
    return ids


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

    samples_path = LAB_PATH + 'GP_Samples/EROS/' + percentage + '%/'
    calculated_feats_path = LAB_PATH + 'Samples_Features/EROS/' + percentage + '%/'

    # Obtengo los archivos con las muestras serializadas
    files = get_paths(samples_path)

    # Obtengo los ids de las curvas que ya han sido calculadas en iteraciones anteriores
    ids = get_ids_in_paths(calculated_feats_path)

    # Puedo especificar las featurs a ocupar o las features a excluir.
    # Depende que sea mas simple
    feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
                    'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
                    'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude',
                    'Q31', 'Rcs', 'Skew', 'SlottedA_length', 'SmallKurtosis',
                    'Std', 'StetsonK','StetsonK_AC']

    exclude_list = None
    
    # feature_list = None 
    # exclude_list = ['Color', 'Eta_color', 'Q31_color', 'StetsonJ', 'StetsonL',
    #                 'CAR_mean', 'CAR_sigma', 'CAR_tau']

    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)

    feat_names = fs.featureList
    del fs

    for f in files:
        eros_id = lu.get_lightcurve_id(f) 

        if eros_id not in ids: 
            print 'Calculando curva: ' + eros_id
            # Las muestras vienen en una tupla, s[0] es una lista con los tiempos de medicion
            # s[1] es una lista de  muestras  donde cada muestra tiene dos
            # arreglos uno para las observaciones y otro para los errores
            aux = open(f, 'r')
            samples = pickle.load(aux)
            aux.close()

            # Estas variables son comunes a todas las muestras
            t_obs = samples[0]
            lc_class = lu.get_lc_class_name(f)

            partial_calc = partial(parallel.calc_sample_feats, t_obs,
                                feature_list=feature_list,
                                   exclude_list=exclude_list)
            error = False
            chunksize = int(100/n_jobs)
            
            # En algunos casos no calza el largo de las mediciones
            if len(t_obs) != len(samples[1][0][0]):
                aux = open(LAB_PATH + 'Samples_Features/EROS/' + percentage + '%/errores.txt', 'a')
                aux.write('No calzan largos de: ' + f + '\n' )
                aux.close()
                continue

            try:
                pool = multiprocessing.Pool(processes=n_jobs, maxtasksperchild=2)
                feature_values = pool.map(partial_calc, samples[1], chunksize)

                pool.close()
                pool.join()

            except Exception as e:
                error = True
                print 'Error: ' + f
                # raise

            if error:
                aux = open(LAB_PATH + 'Samples_Features/EROS/' + percentage + '%/errores.txt', 'a')
                aux.write(f + '\n')
                aux.close()
            else:
                # Escribo los resultados en un archivo especial para cada curva original
                file_path = LAB_PATH + 'Samples_Features/EROS/' + percentage + '%/' + lc_class + '/' + eros_id + '.csv'
                df = pd.DataFrame(feature_values, columns=feat_names)
                df.to_csv(file_path, index=False)
        else:
            print 'Curva: ' + eros_id + 'ya calculada'
