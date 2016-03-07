# coding=utf-8

# Recorre curvas para un porcentaje fijo, las completa
# hasta cierta cantidad de puntos y las guarda
# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
import pandas as pd
import bootstrap

import sys

import FATS

from config import *

catalog = sys.argv[1]
total_points = int(sys.argv[2])

paths = lu.get_lightcurve_paths()
feature_values = []
ids = []

if catalog =='MACHO':
    min_points = 300
elif catalog == 'EROS':
    min_points = 420

percentage = 0.2

for i in xrange(len(paths)):
    path = paths[i]
    lc_id = lu.get_lightcurve_id(path, catalog=catalog)
    clase = lu.get_lightcurve_class(path, catalog=catalog)
    print 'Curva: ' + lc_id

    curva = lu.open_lightcurve(path, catalog=catalog)
    curva = lu.filter_data(curva)

    # Tengo que mantener la consistencia con los sets regulares
    # Aunque esto tal vez se podria evitar con el approach que estoy
    # proponiendo
    if len(curva.index) < min_points:
        continue

    # Tomo el p% de las mediciones
    curva = curva.iloc[0:int(len(curva.index) * percentage)]

    # Esto no me hace sentido pero lo dejo por consistencia
    if curva['err'].nunique() == 1:
        continue

    curva = bootstrap.GP_complete_lc(curva, total_points)

    curva.to_csv('/n/seasfs03/IACS/TSC/ncastro/GP_Curves/' + catalog + '/' +
                 str(int(percentage*100)) + '%/' + str(total_points) + '/' +
                 clase + '/' + lc_id + '.csv')
