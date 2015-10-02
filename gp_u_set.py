# coding=utf-8

# Toma un directorio con archivos de features sampleadas de curvas de luz.
# Para cada set de features sampleadas calcula las gaussianas asociada a cada
# variable. Le agrega la clase y un peso con valor 1 y arma un dataframe y lo
# guarda como set de entrenamiento

# --------------------------------------------------------------------------
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

def calc_gaussian(file_path):
    df = pd.read_csv(file_path)

    num_feats = len(df.columns)

    medias = df.mean()
    std = df.std()
    l = medias - 3*std
    r = medias + 3*std

    medias = medias.tolist()
    std = std.tolist()
    l = l.tolist()
    r = r.tolist()

    linea = []
    for i in xrange(len(medias)):
        linea.append(str(l[i]))
        linea.append(str(medias[i]))
        linea.append(str(r[i]))
        linea.append(str(std[i]))

    linea.append('1.0')
    linea.append(lu.get_lc_class_name(f))

    return ','.join(linea) + '\n'

if __name__ == '__main__':

    if len(sys.argv) == 2:
        percentage = sys.argv[1]
    else:
        percentage = '100'

    output_file_name = 'gp_u_set_' + percentage + '.csv'
    path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%/'

    files = get_paths(path)
    files = [x for x in files]
    print files

    feature_list = pd.read_csv(files[0]).columns.tolist()

    exclude_list = None

    # Elimino features que involucran color y las CAR por temas de tiempo
    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], featureList=feature_list,
                           excludeList=exclude_list)

    linea = []
    for name in fs.featureList:
        linea.append(name + '.l')
        linea.append(name + '.mean')
        linea.append(name + '.r')
        linea.append(name + '.std')
    linea.append('weight')
    linea.append('class')
    linea = ','.join(linea) + '\n'
    f = open(TRAINING_SETS_DIR_PATH + 'GP/' + output_file_name, 'w')
    f.write(linea)
    f.close()

    lineas = [calc_gaussian(f) for f in files]

    f = open(TRAINING_SETS_DIR_PATH + 'GP/' + output_file_name, 'a')
    f.writelines(lineas)
    f.close()
