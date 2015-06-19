# Calcula un set de features para cada curva de la base de datos macho
# Y arma un set de entrenamiento con los valores 

# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd
import numpy as np
import sys

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

paths = paths[0:20]

if len(sys.argv) == 2:
    percentage = int(sys.argv[1])  / float(100)

else:
    print 'No se especifico el porcentaje de las curvas a utilizar'
    percentage = 1

for i in range(len(paths)):
    try:
        path = paths[i]

        # Descarto la banda roja por ahora
        if not 'B.mjd' in path:
            continue

        print 'Curva: ' + lu.get_lightcurve_id(path)

        azul = lu.open_lightcurve(path)

        # Si la curva completa no tiene al menos min_points no la ocupo
        if len(azul.index) < min_points:
            f = open('GP Samples/' + str(int(percentage * 100)) +
                     '%/pocos_puntos.txt', 'a')
            f.write(path + '\n')
            f.close()
            continue

        # Tomo el p% de las mediciones
        azul = azul.iloc[0:int(len(azul) * percentage)]
        total_days = azul.index[-1] - azul.index[0]

        # Preparo la curva para alimentar el GP
        # t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(azul, normalize=False)
        # t_obs = np.ravel(t_obs)
        # y_obs = np.ravel(y_obs)
        # err_obs = np.ravel(err_obs)

        t_obs = azul.index.tolist()
        y_obs = azul['mag'].tolist()
        err_obs = azul['err'].tolist()

        # Calculo algunas features para el grupo de muestras
        sys.stdout.write('Calculando Features...')
        sys.stdout.flush()
        sys.stdout.write('\r')
        sys.stdout.flush()
        
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

    except KeyboardInterrupt:
        raise
    except Exception, e:
        f = open('GP Samples/' + str(int(percentage * 100)) +
                     '%/error.txt', 'a')
        f.write(path + '\n')
        f.close()
        continue

feature_names = fs.result(method='dict').keys()
feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names)

df.sort(axis=1, inplace=True)

df.to_csv(TRAINING_SETS_DIR_PATH + 'Macho regular set ' + str(sys.argv[1]) + '.csv', index=False) 
