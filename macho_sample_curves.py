# coding=utf-8

# Toma una curva genera 100 muestras y las guarda serializadas como un objeto
# -----------------------------------------------------------------------------
import lightcurves.lc_utils as lu
from config import *
import bootstrap

from functools import partial
import multiprocessing
import datetime
import time
import sys

if __name__ == '__main__':

    start_time = time.time()

    if len(sys.argv) == 2:
        percentage = int(sys.argv[1]) / float(100)

    else:
        # print 'No se especifico el porcentaje de las curvas a utilizar'
        percentage = 1.0

    paths = lu.get_lightcurve_paths()
    # paths = [paths[i] for i in[199, 201, 203, 215]]
    paths = [x for x in paths if 'R.mjd' not in x]

    partial_sample = partial(bootstrap.GP_bootstrap, percentage=percentage,
                             n_samples=100)

    pool = multiprocessing.Pool(processes=2)
    pool.map(partial_sample, paths[0:4])

    pool.close()
    pool.join()


    end_time = time.time()

    print 'Tiempo: ' + str(datetime.timedelta(0,end_time - start_time))