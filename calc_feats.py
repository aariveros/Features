# coding=utf-8

# Calcula un set de features para cada curva
# Y arma un set de entrenamiento con los valores 

# -----------------------------------------------------------------------------

# from functools import partial
# import multiprocessing
import argparse
import random
import sys
import os

import pandas as pd
import numpy as np
import FATS

import lightcurves.lc_utils as lu
from config import *

if __name__ == '__main__':
    
    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Calc features to lightcurves and form dataset')
    parser.add_argument('--percentage', required=True, type=str)
    parser.add_argument('--sampling', required=True, type=str)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS', 'OGLE', 'CATALINA', 'ASAS'])
    parser.add_argument('--min_points', required=True, default=300, type=int)
    parser.add_argument('--feature_list', required=False, nargs='*', type=str)
    parser.add_argument('--exclude_list', required=False, nargs='*', type=str)
    parser.add_argument('--save_path', required=True, type=str)
    # parser.add_argument('--n_processes', required=True, type=int)
    
    args = parser.parse_args(sys.argv[1:])

    percentage = int(args.percentage) / float(100)
    sampling = args.sampling
    catalog = args.catalog
    min_points = args.min_points
    feature_list = args.feature_list
    exclude_list = args.exclude_list
    save_path = args.save_path
    # n_processes = args.n_processes

    random.seed(1)

    paths = lu.get_lightcurve_paths(catalog=catalog)
    # paths = paths[0:20]
    feature_values = []
    lc_ids = []

    pocos_path = TRAINING_SETS_DIR_PATH + 'problemas/pocos_puntos ' +
                      str(int(percentage * 100)) + '.txt'
    errores_path = TRAINING_SETS_DIR_PATH + 'problemas/errores ' +
                      str(int(percentage * 100)) + '.txt'

    if os.path.isfile(pocos_path):
        os.remove(pocos_path)

    if os.path.isfile(errores_path):
        os.remove(errores_path)

    pocos_puntos_file = open(pocos_path, 'a')
    errores_file = open(errores_path, 'a')

    for path in paths:
        try:

            lc_id = lu.get_lightcurve_id(path, catalog=catalog)
            print 'Curva: ' + lc_id

            # Para filtrar a solo algunas clases
            lc_class = lu.get_lightcurve_class(path, catalog=catalog)
            # if lc_class not in ['EB', 'Be_lc']:
            #     continue

            lc = lu.open_lightcurve(path, catalog=catalog)
            lc = lu.filter_data(lc)

            # Si la curva filtrada no tiene al menos min_points no la ocupo
            if len(lc.index) < min_points:
                pocos_puntos_file.write(path + '\n')
                continue

            # Tomo el p% de las mediciones
            n_obs = int(lc.index.size * percentage)
            if sampling == 'normal':
                lc = lc.iloc[0:n_obs]
            elif sampling == 'new':
                lc = lc.iloc[np.linspace(0, lc.index.size-1, num=n_obs, dtype=int)]
            elif sampling == 'uniform':
                aux_indices = random.sample(range(len(lc.index)), n_obs)
                aux_indices.sort()
                lc = lc.iloc[aux_indices]

            t_obs = lc.index.tolist()
            y_obs = lc['mag'].tolist()
            err_obs = lc['err'].tolist()
            
            fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)
            fs = fs.calculateFeature([y_obs, t_obs, err_obs])

            valores = map(lambda x: float("{0:.6f}".format(x)),fs.result(method='dict').values())
            valores.append(lc_class)

            feature_values.append(valores)
            lc_ids.append(lc_id)

        except KeyboardInterrupt:
            raise
        except Exception, e:
            errores_file.write(path + '\n')
            continue
    
    errores_file.close()
    pocos_puntos_file.close()

    feature_names = fs.result(method='dict').keys()
    feature_names.append('class')
    df = pd.DataFrame(feature_values, columns=feature_names, index=lc_ids)

    # Porque sorteo??
    df.sort(axis=1, inplace=True)

    df.to_csv(save_path) 
