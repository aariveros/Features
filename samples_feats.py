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
import numpy as np
import FATS

import lightcurves.lc_utils as lu
from config import *
import parallel


if __name__ == '__main__':
    
    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Get bootstrap samples from lightcurves')
    parser.add_argument('--n_processes', required=True, type=int)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS', 'OGLE', 'CATALINA'])
    parser.add_argument('--feature_list',  nargs='*', type=str)
    parser.add_argument('--exclude_list',  nargs='*', type=str)
    parser.add_argument('--samples_path', required=True, type=str)
    parser.add_argument('--calculated_feats_path', required=True, type=str)

    args = parser.parse_args(sys.argv[1:])

    catalog = args.catalog
    n_processes = args.n_processes
    feature_list = args.feature_list
    exclude_list = args.exclude_list
    samples_path = args.samples_path
    calculated_feats_path = args.calculated_feats_path

    print feature_list

    if os.path.isfile(calculated_feats_path + 'errores.txt'):
        os.remove(calculated_feats_path + 'errores.txt')

    # Obtengo los archivos con las muestras serializadas
    files = lu.get_paths(samples_path, '.pkl')

    # Obtengo los ids de las curvas que ya han sido calculadas en iteraciones anteriores
    ids = lu.get_ids_in_path(calculated_feats_path, catalog=catalog, extension='.csv')


    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)

    feat_names = fs.featureList
    del fs

    error_file = open(calculated_feats_path + 'errores.txt', 'a')

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
                print 'EOFError - ' + lc_id
                error_file.write(f + '\n')
                continue
            except KeyError as ke:
                print 'KeyError - ' + lc_id
                error_file.write(f + '\n')
                continue
            except Exception as e:
                print 'Unknown error - ' + lc_id
                error_file.write(f + '\n')
                continue

            # Estas variables son comunes a todas las muestras
            t_obs = samples[0]
            lc_class = lu.get_lightcurve_class(f, catalog=catalog)

            partial_calc = partial(parallel.calc_sample_feats, t_obs,
                                   feature_list=feature_list,
                                   exclude_list=exclude_list)
            error = False
            chunksize = int(100/n_processes)
            
            # Algunos casos de errores raros en las curvas sampleadas
            if len(t_obs) != len(samples[1][0][0]):
                print 'Error de largos - ' + lc_id
                error_file.write('No calzan largos de: ' + f + '\n' )
                continue
            elif len(set(samples[1][0][1])) == 1:
                print 'Errores == 0 - ' + lc_id
                error_file.write('Todas las observaciones con el mismo error: ' + f + '\n')
                continue
            elif np.isnan(samples[1][0][0]).any():
                print 'Error de Nan en y_obs - ' + lc_id
                error_file.write('Observaciones Nan: ' + f + '\n' )
                continue

            try:
                pool = multiprocessing.Pool(processes=n_processes,
                                            maxtasksperchild=2)
                feature_values = pool.map(partial_calc, samples[1], chunksize)
                #feature_values = map(partial_calc, samples[1])
                pool.close()
                pool.join()

            except Exception as e:
                error = True
                print 'Error: ' + f
                # raise
            if error:
                error_file.write(f + '\n')
            else:
                # Escribo los resultados en un archivo especial para cada curva original
                file_path = (calculated_feats_path + lc_class + '/' + lc_id +
                             '.csv')
                df = pd.DataFrame(feature_values, columns=feat_names)
                df.to_csv(file_path, index=False)
        else:
            pass
            # print 'Curva: ' + lc_id + ' - ya calculada'

    error_file.close()
