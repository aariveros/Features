# coding=utf-8

# Toma un directorio con muestras sampleadas de curvas de luz y para cada 
# una calcula un set de Features, y guarda un dataframe con los valores en
# algun directorio

# --------------------------------------------------------------------------

from functools import partial
import multiprocessing
import argparse
import pickle
import sys
import os

import pandas as pd
import FATS

import lightcurves.lc_utils as lu
from config import *
import parallel


if __name__ == '__main__':
    
    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Get bootstrap samples from lightcurves')
    parser.add_argument('--percentage', required=True, type=str)
    parser.add_argument('--n_processes', required=True, type=int)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS', 'OGLE'])
    parser.add_argument('--feature_list',  nargs='*', type=str)
    parser.add_argument('--sampling', required=True, type=str)

    args = parser.parse_args(sys.argv[1:])

    percentage = args.percentage
    catalog = args.catalog
    n_processes = args.n_processes
    feature_list = args.feature_list
    sampling = args.sampling

    print feature_list

    samples_path = LAB_PATH + 'GP_Samples/' + catalog + '/' + sampling + '/' + percentage + '%/'
    calculated_feats_path = LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling + '/' + percentage + '%/'

    if os.path.isfile(LAB_PATH + 'Samples_Features/' + catalog + '/' +
                      sampling + '/' + percentage + '%/errores.txt'):
        os.remove(LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling +
                  '/' + percentage + '%/errores.txt')

    # Obtengo los archivos con las muestras serializadas
    files = lu.get_paths(samples_path, '.pkl')

    # Obtengo los ids de las curvas que ya han sido calculadas en iteraciones anteriores
    ids = lu.get_ids_in_path(calculated_feats_path, catalog=catalog, extension='.csv')

    exclude_list = None
    
    # feature_list = None 
    # exclude_list = ['Color', 'Eta_color', 'Q31_color', 'StetsonJ', 'StetsonL',
    #                 'CAR_mean', 'CAR_sigma', 'CAR_tau']

    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)

    feat_names = fs.featureList
    del fs

    for f in files:
        lc_id = lu.get_lightcurve_id(f, catalog=catalog) 

        if lc_id not in ids: 
            print 'Calculando curva: ' + lc_id
            # Las muestras vienen en una tupla, s[0] es una lista con los tiempos de medicion
            # s[1] es una lista de  muestras  donde cada muestra tiene dos
            # arreglos uno para las observaciones y otro para los errores
            
            try:
                aux = open(f, 'rb')
                samples = pickle.load(aux)
                aux.close()
            except EOFError as e:
                aux = open(LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling + '/' +
                           percentage + '%/errores.txt', 'a')
                aux.write(f + '\n')
                aux.close()
                continue

            # Estas variables son comunes a todas las muestras
            t_obs = samples[0]
            lc_class = lu.get_lightcurve_class(f, catalog=catalog)

            partial_calc = partial(parallel.calc_sample_feats, t_obs,
                                   feature_list=feature_list,
                                   exclude_list=exclude_list)
            error = False
            chunksize = int(100/n_processes)
            
            # En algunos casos no calza el largo de las mediciones
            if len(t_obs) != len(samples[1][0][0]):
                aux = open(LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling + '/' +
                           percentage + '%/errores.txt', 'a')
                aux.write('No calzan largos de: ' + f + '\n' )
                aux.close()
                continue

            try:
                #pool = multiprocessing.Pool(processes=n_processes,
                #                            maxtasksperchild=2)
                #feature_values = pool.map(partial_calc, samples[1], chunksize)
                #pool.close()
                #pool.join()
                feature_values = map(partial_calc, samples[1], chunksize)

            except Exception as e:
                error = True
                print 'Error: ' + f
                # raise

            if error:
                aux = open(LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling + '/' +
                           percentage + '%/errores.txt', 'a')
                aux.write(f + '\n')
                aux.close()
            else:
                # Escribo los resultados en un archivo especial para cada curva original
                file_path = (LAB_PATH + 'Samples_Features/' + catalog + '/' + sampling + '/' +
                             percentage + '%/' + lc_class + '/' + lc_id +
                             '.csv')
                df = pd.DataFrame(feature_values, columns=feat_names)
                df.to_csv(file_path, index=False)
        else:
            print 'Curva: ' + lc_id + 'ya calculada'
