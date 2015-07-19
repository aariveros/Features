# coding=utf-8

# Script para coregir errores del primer sampleo que hice en el cluster. 
# Agrega los tiempos de las observaciones de las curvas de luz

# -----------------------------------------------------------------------------
import numpy as np

import pickle
import sys
import os

import lightcurves.lc_utils as lu
from config import *

def absoluteFilePaths(directory):
    """Busca en el directorio todos los archivos que corresponden a muestras
    obtenidas de curvas de luz
    """
    files = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                files.append(f)

    return files

def filterObservations(lc):
    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)
    t_obs = np.ravel(t_obs)
    return t_obs

if len(sys.argv) == 2:
    percentage = int(sys.argv[1])  / float(100)

else:
    print 'No se especifico el porcentaje de las curvas a utilizar'
    percentage = 1.0


lc_paths = lu.get_lightcurve_paths()
lc_paths = [x for x in lc_paths if 'R.mjd' not in x]
samples_dir = LAB_PATH + 'GP_Samples/MACHO/' + str(int(percentage*100)) + '%/'
samples_files = absoluteFilePaths(samples_dir)

for sample_file in samples_files:
    id = sample_file.replace(' samples.pkl', '')
    for lc_path in lc_paths:
        if id in lc_path:
            current_lc_path = lc_path
            break

    lc = lu.open_lightcurve(current_lc_path)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    t_obs = filterObservations(lc)

    f = open(samples_dir + sample_file)
    samples = pickle.load(f)
    f.close()
    clase = lu.get_lc_class_name(current_lc_path)

    f = open(samples_dir + clase + '/' + sample_file, 'wb')
    new_sample = (t_obs, samples)
    pickle.dump(new_sample, f)
    f.close()



