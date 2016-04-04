# coding=utf-8

# Calcula un set de features para cada curva sacada de la media de un 
# GP ajustado sobre las curvas de MACHO

# -----------------------------------------------------------------------------

import os
import sys
import pickle
import argparse
import multiprocessing
from functools import partial

import FATS
import pandas as pd

import parallel
from config import *
import lightcurves.lc_utils as lu


# Recibo parámetros de la linea de comandos
print ' '.join(sys.argv)
parser = argparse.ArgumentParser(
    description='Get bootstrap samples from lightcurves')
parser.add_argument('--percentage', required=True, type=str)
parser.add_argument('--n_processes', required=True, type=int)
parser.add_argument('--catalog', default='MACHO',
                    choices=['MACHO', 'EROS', 'OGLE'])
parser.add_argument('--feature_list',  nargs='*', type=str)
parser.add_argument('--samples_path', required=True, type=str)
parser.add_argument('--result_dir', required=True, type=str)

args = parser.parse_args(sys.argv[1:])

percentage = int(args.percentage) / float(100)
catalog = args.catalog
n_processes = args.n_processes
feature_list = args.feature_list
samples_path = args.samples_path
result_dir = args.result_dir

if os.path.isfile(samples_path + 'errores.txt'):
    os.remove(samples_path + 'errores.txt')

error_file = open(samples_path + 'errores.txt', 'a')

paths = lu.get_paths(samples_path, 'pkl')
lc_paths = [x for x in paths]

# Filtro las curvas que no tienen suficientes puntos
aux = []
for p in lc_paths:

    try:
        f = open(p, 'rb')
        lc = pickle.load(f)
        f.close()
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

    y_obs = lc[1].tolist()
    
    if len(y_obs) < 15:
        f = open(samples_path + 'pocos_puntos ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(p + '\n')
        f.close()
        continue
    else:
        aux.append(p)
lc_paths = aux

partial_calc = partial(parallel.calc_feats, feature_list=feature_list,
                       exclude_list=None, percentage=percentage)

pool = multiprocessing.Pool()
values = pool.map(partial_calc, lc_paths)
pool.close()
pool.join()

fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                       featureList=feature_list, excludeList=exclude_list)

feature_names = [catalog + '_id'] + fs.featureList + ['class']

df = pd.DataFrame(values, columns=feature_names)
df = df.set_index(catalog + '_id')
df.sort(axis=1, inplace=True)
df.to_csv(result_dir) 

error_file.close()
