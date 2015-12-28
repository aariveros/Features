# Calcula un set de features para cada curva sacada de la media de un 
# GP ajustado sobre las curvas de MACHO

# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd
import pickle
import numpy as np
import sys
import os

from functools import partial
import multiprocessing

import FATS

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
min_points = 300
feature_values = []
macho_ids = []

paths = paths[0:20]

if os.path.isfile(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt'):
    os.remove(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt')

for path in paths:
    try:

        macho_id = lu.get_lightcurve_id(path)
        print 'Curva: ' + lu.get_lightcurve_id(path)

        macho_class = lu.get_lc_class_name(path)

        f = open(path, 'rb')
        lc = pickle.load(f)
        f.close()

        aux = {'mag':lc[1], 'err':lc[2]}
        lc = pd.DataFrame(aux, index=lc[0])

        lc = lu.filter_data(lc)

        # Si la curva filtrada no tiene al menos min_points no la ocupo
        if len(lc.index) < min_points:
            f = open(sets_dir_path + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt', 'a')
            f.write(path + '\n')
            f.close()
            continue

        # Tomo el p% de las mediciones
        lc = lc.iloc[0:int(len(lc) * percentage)]

        t_obs = lc.index.tolist()
        y_obs = lc['mag'].tolist()
        err_obs = lc['err'].tolist()
        
        # Elimino features que involucran color y las CAR por temas de tiempo
        fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                               featureList=None, excludeList=['Color',
                               'Eta_color', 'Q31_color', 'StetsonJ',
                               'StetsonL', 'CAR_mean', 'CAR_sigma', 'CAR_tau'])
        
        fs = fs.calculateFeature([y_obs, t_obs, err_obs])

        valores = map(lambda x: float("{0:.6f}".format(x)),fs.result(method='dict').values())
        valores.append(macho_class)

        feature_values.append(valores)
        macho_ids.append(macho_id)

    except KeyboardInterrupt:
        raise
    except Exception, e:
        f = open(sets_dir_path + 'problemas/errores ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(path + '\n')
        f.close()
        continue

feature_names = fs.result(method='dict').keys()
feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names, index=macho_ids)

df.sort(axis=1, inplace=True)

df.to_csv('/n/home09/ncastro/workspace/Features/sets/MACHO_Means/Macho means set ' + str(sys.argv[1]) + '.csv') 