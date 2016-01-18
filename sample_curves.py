# coding=utf-8

# Toma una curva genera 100 muestras y las guarda serializadas como un objeto
# -----------------------------------------------------------------------------

import lightcurves.lc_utils as lu
from config import *
import bootstrap
import cPickle

import numpy as np

from functools import partial
import multiprocessing
import sys

def sample_curve(lc_path, catalog='MACHO', percentage=1.0, sampling='equal', n_samples=100):
    """Este metodo es un wrapper que abre una curva, la preprocesa,
    saca muestras con un GP y después las guarda en algún lugar.
    """
    lc = lu.open_lightcurve(lc_path, catalog=catalog)
    lc = lu.filter_data(lc)
    lc = lc.iloc[0:int(percentage * lc.index.size)]

    t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

    var = np.var(y_obs)
    l = 6 * (max_time - min_time) / float(lc.index[-1] - lc.index[0])
    kernel = var ** 2 * kernels.ExpSquaredKernel(l ** 2)

    samples_devs = bootstrap.GP_bootstrap(lc, kernel, sampling, n_samples)

    result_dir = (LAB_PATH + 'GP_Samples/' + catalog + '/' + sampling + '/' +
                      str(int(100 * percentage)) + '%/' + 
                      lu.get_lightcurve_class(lc_path, catalog=catalog) + '/' +
                      lu.get_lightcurve_id(lc_path, catalog=catalog) +
                      ' samples.pkl')

    output = open(result_dir, 'wb')
    cPickle.dump(samples_devs, output)
    output.close()

if __name__ == '__main__':

    percentage = int(sys.argv[1]) / float(100)
    catalog = sys.argv[2]
    sampling = sys.argv[3]

    paths = lu.get_lightcurve_paths(catalog=catalog)
    
    if catalog == 'MACHO':
        paths = [x for x in paths if 'R.mjd' not in x]

    partial_sample = partial(sample_curve, catalog=catalog,
                             percentage=percentage, sampling=sampling,
                             n_samples=100)

    pool = multiprocessing.Pool(processes=2)
    pool.map(partial_sample, paths[0:4])

    pool.close()
    pool.join()