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

if __name__ == '__main__':

    if len(sys.argv) == 2:
        percentage = int(sys.argv[1]) / float(100)

    else:     
        percentage = 1.0

    n_jobs = 30

    result_dir = LAB_PATH + 'GP_Means/MACHO/' + str(int(100 * percentage)) + '%/'

    paths = lu.get_lightcurve_paths()
    paths = [x for x in paths if 'R.mjd' not in x]

    partial_sample = partial(bootstrap.GP_sample_mean, result_dir=result_dir,
    						 percentage=percentage)

    pool = multiprocessing.Pool(processes=n_jobs)
    pool.map(partial_sample, paths)

    pool.close()
    pool.join()