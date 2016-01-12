# Calcula un set de features para cada curva de la base de datos EROS
# Y arma un set de entrenamiento con los valores 

# -----------------------------------------------------------------------------

import lightcurves.eros_utils as lu
import pandas as pd
import sys

import FATS

from config import *

paths = lu.get_lightcurve_paths()
min_points = 420
feature_values = []

# paths = paths[0:20]

if len(sys.argv) == 2:
    percentage = int(sys.argv[1])  / float(100)

else:
    print 'No se especifico el porcentaje de las curvas a utilizar'
    percentage = 1

for i in range(len(paths)):
    try:
        path = paths[i]

        print 'Curva: ' + lu.get_lightcurve_id(path)

        curva = lu.open_lightcurve(path)
        curva = lu.filter_data(curva)

        # Si la curva filtrada no tiene al menos min_points no la ocupo
        if len(curva.index) < min_points:
            f = open(TRAINING_SETS_DIR_PATH + 'problemas/pocos_puntos_eros ' + str(int(percentage * 100)) + '.txt', 'a')
            f.write(path + '\n')
            f.close
            continue

        # Tomo el p% de las mediciones
        curva = curva.iloc[0:int(len(curva) * percentage)]
        total_days = curva.index[-1] - curva.index[0]

        if curva['err'].nunique() == 1:
            continue

        t_obs = curva.index.tolist()
        y_obs = curva['mag'].tolist()
        err_obs = curva['err'].tolist()

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
        f = open(TRAINING_SETS_DIR_PATH + 'problemas/errores_eros ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(path + '\n')
        f.close()
        continue

feature_names = fs.result(method='dict').keys()
feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names)

df.sort(axis=1, inplace=True)

df.to_csv(TRAINING_SETS_DIR_PATH + 'EROS/EROS regular set ' + str(sys.argv[1]) + '.csv', index=False) 
