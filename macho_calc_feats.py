# Calcula un set de features para cada curva de la base de datos macho
# Y arma un set de entrenamiento con los valores 

# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd
import numpy as np
import sys
import os

from functools import partial
import multiprocessing

import FATS

from config import *

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

paths = lu.get_lightcurve_paths()
min_points = 300
feature_values = []
macho_ids = []

# paths = paths[0:20]

if len(sys.argv) == 2:
    percentage = int(sys.argv[1])  / float(100)

else:
    print 'No se especifico el porcentaje de las curvas a utilizar'
    percentage = 1

if os.path.isfile(TRAINING_SETS_DIR_PATH + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt'):
    os.remove(TRAINING_SETS_DIR_PATH + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt')

for path in paths:
    try:
        
        # Descarto la banda roja por ahora
        if not 'B.mjd' in path:
            continue

        macho_id = lu.get_lightcurve_id(path)
        print 'Curva: ' + lu.get_lightcurve_id(path)

        macho_class = lu.get_lc_class_name(path)
        if macho_class not in ['EB', 'Be_lc']:
            continue

        azul = lu.open_lightcurve(path)
        azul = lu.filter_data(azul)

        # Si la curva filtrada no tiene al menos min_points no la ocupo
        if len(azul.index) < min_points:
            f = open(TRAINING_SETS_DIR_PATH + 'problemas/pocos_puntos ' + str(int(percentage * 100)) + '.txt', 'a')
            f.write(path + '\n')
            f.close()
            continue

        # Tomo el p% de las mediciones
        azul = azul.iloc[0:int(len(azul) * percentage)]
        total_days = azul.index[-1] - azul.index[0]

        t_obs = azul.index.tolist()
        y_obs = azul['mag'].tolist()
        err_obs = azul['err'].tolist()
        
        # Elimino features que involucran color y las CAR por temas de tiempo
        fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                               featureList=None, excludeList=['Color',
                               'Eta_color', 'Q31_color', 'StetsonJ',
                               'StetsonL', 'CAR_mean', 'CAR_sigma', 'CAR_tau'])
        
        fs = fs.calculateFeature([y_obs, t_obs, err_obs])

        clase = lu.get_lc_class_name(path)
        valores = map(lambda x: float("{0:.6f}".format(x)),fs.result(method='dict').values())
        valores.append(clase)

        feature_values.append(valores)
        macho_ids.append(macho_id)

    except KeyboardInterrupt:
        raise
    except Exception, e:
        f = open(TRAINING_SETS_DIR_PATH + 'problemas/errores ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(path + '\n')
        f.close()
        continue

feature_names = fs.result(method='dict').keys()
feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names, index=macho_ids)

df.sort(axis=1, inplace=True)

df.to_csv(TRAINING_SETS_DIR_PATH + '/MACHO_Reduced/Macho reduced set ' + str(sys.argv[1]) + '.csv') 
