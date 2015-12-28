# coding=utf-8

# Le ajusta un GP a un set de curvas y guarda los valores medios del modelo
# para los ptos donde hay observaciones
# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
from config import *
import bootstrap

from functools import partial
import multiprocessing
import sys
import os

def get_ids_in_paths(directory):
    """Busca todos los .pkl de un directorio, encuentra los ids y los retorna
    """
    ids = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.pkl' in f:
                ids.append(lu.get_lightcurve_id(os.path.abspath(os.path.join(dirpath, f))))
    return ids

if __name__ == '__main__':

    if len(sys.argv) == 2:
        percentage = int(sys.argv[1]) / float(100)

    else:
        percentage = 1.0

    n_jobs = 30

    result_dir = LAB_PATH + 'GP_Means/MACHO/' + str(int(100 * percentage)) + '%/'
    # Obtengo los ids de las curvas que ya han sido calculadas en iteraciones anteriores
    ids = get_ids_in_paths(result_dir)

    paths = lu.get_lightcurve_paths()
    paths = [x for x in paths if 'R.mjd' not in x]
    paths = [x for x in paths if lu.get_lightcurve_id(x) not in ids]

    partial_sample = partial(bootstrap.GP_sample_mean, result_dir=result_dir,
    						 percentage=percentage)

    pool = multiprocessing.Pool(processes=n_jobs)
    pool.map(partial_sample, paths)

    pool.close()
    pool.join()
