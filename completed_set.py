import lightcurves.eros_utils as lu
import pandas as pd
import bootstrap

import sys

import FATS

from config import *


paths = lu.get_lightcurve_paths()

feature_values = []
ids = []
min_points = 300

if len(sys.argv) == 2:
    total_points = int(sys.argv[1])

else:
    print 'No se especifico el numero de puntos a utilizar'
    total_points = 700

percentage = '20'

for i in xrange(paths):
    try:
        path = paths[i]
        print 'Curva: ' + lu.get_lightcurve_id(path)

        curva = lu.open_lightcurve(path)
        curva = lu.filter_data(curva)

        # Tengo que mantener la consistencia con los sets regulares de EROS
        # Aunque esto tal vez se podria evitar con el approach que estoy
        # proponiendo
        if len(curva.index) < min_points:
            continue

        # Tomo el p% de las mediciones
        curva = curva.iloc[0:int(len(curva) * percentage)]
        total_days = curva.index[-1] - curva.index[0]

        # Esto no me hace sentido pero lo dejo por consistencia
        if curva['err'].nunique() == 1:
            continue

        curva = bootstrap.GP_complete_lc(curva, total_points)

        t_obs = curva.index.tolist()
        y_obs = curva['mag'].tolist()
        err_obs = curva['err'].tolist()

        # Elimino features que involucran color y las CAR por temas de tiempo
        fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'],
                               featureList=None, excludeList=['Color',
                               'Eta_color', 'Q31_color', 'StetsonJ',
                               'StetsonL', 'CAR_mean', 'CAR_sigma', 'CAR_tau'])

        fs = fs.calculateFeature([y_obs, t_obs, err_obs])

        clase = lu.get_lc_class_name(path)
        valores = map(lambda x: float("{0:.6f}".format(x)),fs.result(method='dict').values())
        valores.append(clase)

        ids.append(lu.get_lightcurve_id(path))

        feature_values.append(valores)

    except KeyboardInterrupt:
        raise
    except Exception, e:
        f = open('/n/seasfs03/IACS/TSC/ncastro/GP_Sets/EROS/problemas/GP_completo_eros ' + str(int(percentage * 100)) + '.txt', 'a')
        f.write(path + '\n')
        f.close()
        continue

    feature_names = fs.result(method='dict').keys()
    feature_names.append('class')
    df = pd.DataFrame(feature_values, columns=feature_names, index=ids)

    df.sort(axis=1, inplace=True)

    df.to_csv('/n/seasfs03/IACS/TSC/ncastro/GP_Sets/EROS/' + percentage + '%/EROS_completed_set_' + total_points + '.csv') 

