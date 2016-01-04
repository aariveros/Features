# Calcula un set de features para cada curva sacada de la media de un 
# GP ajustado sobre las curvas de MACHO

# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd
import pickle
import FATS
import sys
import os

from functools import partial
import multiprocessing
import parallel

from config import *

def get_paths(directory):
    """Entrega todos los paths absolutos a objetos serializados de un directorio
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                yield(os.path.abspath(os.path.join(dirpath, f)))

if len(sys.argv) == 2:
    percentage = int(sys.argv[1])  / float(100)

else:
    print 'No se especifico el porcentaje de las curvas a utilizar'
    percentage = 1

sets_dir_path = '/n/seasfs03/IACS/TSC/ncastro/GP_Means/MACHO/'

paths = get_paths(sets_dir_path + str(int(percentage * 100)) + '%/')
lc_paths = [x for x in paths]

if os.path.isfile(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt'):
    os.remove(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt')

# Filtro las curvas que no tienen suficientes puntos
aux = []
for p in lc_paths:
    f = open(p, 'rb')
    lc = pickle.load(f)
    f.close()

    y_obs = lc[1].tolist()
    
    if len(y_obs) < 15:
        f = open(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(p + '\n')
        f.close()
        continue
    else:
        aux.append(p)
lc_paths = aux

feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
                'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
                'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'Q31', 'Rcs', 'Skew',
                'SlottedA_length', 'SmallKurtosis', 'Std', 'StetsonK', 'StetsonK_AC']

# Elimino features que involucran color y las CAR por temas de tiempo
exclude_list=['Color', 'Eta_color', 'Q31_color', 'StetsonJ', 'StetsonL',
             'CAR_mean', 'CAR_sigma', 'CAR_tau']

partial_calc = partial(parallel.calc_feats, feature_list=feature_list,
                       exclude_list=exclude_list, percentage=percentage)

pool = multiprocessing.Pool()
values = pool.map(partial_calc, lc_paths)
pool.close()
pool.join()

fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                       featureList=feature_list, excludeList=exclude_list)

feature_names = ['macho_id'] + fs.featureList + ['class']

df = pd.DataFrame(values, columns=feature_names)
df = df.set_index('macho_id')
df.sort(axis=1, inplace=True)
df.to_csv('/n/home09/ncastro/workspace/Features/sets/MACHO_Means/Macho means set ' + str(sys.argv[1]) + '.csv') 
