# coding=utf-8

# Toma un directorio con archivos de features sampleadas de curvas de luz
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
            if '.pkl' in f:
                yield os.path.abspath(os.path.join(dirpath, f))

if len(sys.argv) == 2:
    percentage = sys.argv[1]
else:
    percentage = '100'

output_file_name = 'gp_u_set_' + percentage + '.csv'

# Elimino features que involucran color y las CAR por temas de tiempo
fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], featureList=None,
                       excludeList=['Color', 'Eta_color', 'Q31_color',
                       'StetsonJ','StetsonL', 'CAR_mean', 'CAR_sigma', 'CAR_tau'])

linea = []
for name in fs.featureList:
    linea.append(name+'.l')
    linea.append(name+'.mean')
    linea.append(name+'.r')
    linea.append(name+'.std')
linea.append('weight')
linea.append('class')
linea = ','.join(linea) + '\n'
f = open(TRAINING_SETS_DIR_PATH + 'GP/' + output_file_name, 'w')
f.write(linea)
f.close()

path = LAB_PATH + 'GP_Samples/MACHO/' + percentage + '%'
files = get_paths(path)

lineas = []

for f in files:
    df = pd.read_csv(f)

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

    lineas.append(','.join(linea) + '\n')

f = open(output_file_name, 'a')
f.writelines(lineas)
f.close()