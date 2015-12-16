# coding=utf-8

# Recorre las curvas de EROS para un porcentaje fijo, las completa
# hasta cierta cantidad de puntos y las guarda
# -----------------------------------------------------------------------------

import lightcurves.eros_utils as lu
import pandas as pd
import bootstrap

import sys

import FATS

from config import *


paths = lu.get_lightcurve_paths()

feature_values = []
ids = []
min_points = 420

if len(sys.argv) == 2:
    total_points = int(sys.argv[1])

else:
    print 'No se especifico el numero de puntos a utilizar'
    total_points = 700

percentage = 0.2

for i in xrange(len(paths)):
    path = paths[i]
    eros_id = lu.get_lightcurve_id(path)
    clase = lu.get_lc_class_name(path)
    print 'Curva: ' + eros_id

    curva = lu.open_lightcurve(path)
    curva = lu.filter_data(curva)

    # Tengo que mantener la consistencia con los sets regulares de EROS
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

    curva.to_csv('/n/seasfs03/IACS/TSC/ncastro/GP_Curves/EROS/' + str(int(percentage*100)) + '%/' + str(total_points) + '/' + clase + '/' + eros_id + '.csv')
