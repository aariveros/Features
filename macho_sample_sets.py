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

    files = get_paths(samples_path)
    files = [x for x in files]
    ids = [lu.get_lightcurve_id(x) for x in files]

    feature_list = pd.read_csv(files[0]).columns.tolist()
    feature_list.append('class')
    linea = ','.join(feature_list) + '\n'

    for i in xrange(100):
        f = open('/n/seasfs03/IACS/TSC/ncastro/sets/MACHO_Sampled/' + percentage
                 + '%/' + 'macho_sampled_' + str(i) + '.csv', 'w')
        f.write(linea)
        f.close()

    # dfs = [pd.read_csv(f) for f in files]

    # for i in xrange(len(dfs[0].index)):
    #     rows = [df.iloc[i] for df in dfs]
    #     pd.concatenate[rows]
    #     pd.to_csv()
