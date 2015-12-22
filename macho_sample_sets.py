# coding=utf-8

# Toma un directorio con archivos de features sampleadas de curvas de luz.
# Con ellos separo los valores de las features en n sets de entrenamiento
# distintos. Donde n es el numero de muestras

# -----------------------------------------------------------------------------
import sys
import os

import pandas as pd
import FATS

import lightcurves.lc_utils as lu
from config import *

def get_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.csv' in f:
                yield os.path.abspath(os.path.join(dirpath, f))

if __name__ == '__main__':
    if len(sys.argv) == 2:
        percentage = sys.argv[1]
    else:
        percentage = '100'

    samples_path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%/'

    feature_samples_files = get_paths(samples_path)
    feature_samples_files = [x for x in feature_samples_files]
    ids = [lu.get_lightcurve_id(x) for x in feature_samples_files]

    feature_list = ['']
    feature_list.extend(pd.read_csv(feature_samples_files[0]).columns.tolist())
    feature_list.append('class')
    linea = ','.join(feature_list) + '\n'

    archivos = []
    for i in xrange(100):
        f = open('/n/seasfs03/IACS/TSC/ncastro/sets/MACHO_Sampled/' + percentage
                 + '%/' + 'macho_sampled_' + str(i) + '.csv', 'w')
        f.write(linea)
        archivos.append(f)
    
    for f in feature_samples_files:
        macho_id = lu.get_lightcurve_id(f)
        macho_class = lu.get_lc_class_name(f)

        archivo = open(f, 'r')

        # Boto la prima linea con el nombre de las columnas
        archivo.readline()

        for index, l in enumerate(archivo):
            linea = [macho_id]
            linea.extend(l.strip('\n').split(','))
            linea.append(macho_class)
            linea = ','.join(linea) + '\n'

            archivos[index].write(linea)
    
    for f in archivos:
        f.close()
