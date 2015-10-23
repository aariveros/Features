# coding=utf-8

# --------------------------------------------------------------------------

from config import *

import pickle
import os

import numpy as np

def get_paths(directory):
    """Entrega todos los paths absolutos a objetos serializados de un directorio
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                yield(os.path.abspath(os.path.join(dirpath, f)))

for p in [5,10,15,20]:
    percentage = str(p)
    samples_path = LAB_PATH + 'GP_Samples/EROS/' + percentage + '%/'
    files = get_paths(samples_path)

    for f in files:
        aux = open(f, 'r')
        samples = pickle.load(aux)
        aux.close()

        errores = samples[1][0][1]

        if np.all(errores == np.zeros(len(errores))):
            archivo = open(LAB_PATH + 'GP_Samples/EROS/' + percentage + '%/error_eros.txt', 'a')
            archivo.write(f + '\n')
            archivo.close()

            os.remove(f)
