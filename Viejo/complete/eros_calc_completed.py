import lightcurves.eros_utils as lu
import pandas as pd
import bootstrap

import sys
import os

import FATS

from config import *

def absoluteFilePaths(directory):
    paths = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.csv' in f:
                paths.append(os.path.abspath(os.path.join(dirpath, f)))
    return paths

if len(sys.argv) == 2:
    total_points = int(sys.argv[1])

percentage = 0.2

feature_values = []
ids = []

paths = absoluteFilePaths('/n/seasfs03/IACS/TSC/ncastro/GP_Curves/EROS/' + str(int(percentage*100)) + '%/' + str(total_points) + '/')

for i in xrange(len(paths)):
    path = paths[i]
    sys.stdout.write(path + '\n')

    curva = pd.read_csv(path, index_col=0)

    # Esto no me hace sentido pero lo dejo por consistencia
    if curva['err'].nunique() == 1:
        continue

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

feature_names = fs.result(method='dict').keys()
feature_names.append('class')
df = pd.DataFrame(feature_values, columns=feature_names, index=ids)

df.sort(axis=1, inplace=True)

df.to_csv('/n/seasfs03/IACS/TSC/ncastro/GP_Sets/EROS/' + str(int(percentage*100)) + '%/EROS_completed_set_' + str(total_points) + '.csv') 

