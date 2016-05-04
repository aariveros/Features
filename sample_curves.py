# coding=utf-8

# Toma una curva genera muestras y las guarda serializadas como un objeto
# -----------------------------------------------------------------------------

import os
import sys
import cPickle
import argparse
import multiprocessing
from functools import partial

import numpy as np
from george import kernels

import optimize
import bootstrap
from config import *
import lightcurves.lc_utils as lu


def sample_curve(lc_path, catalog='MACHO', percentage=1.0, sampling='equal',
                 lc_sampling='normal', n_samples=100, param_choice='fitted',
                 samples_path=''):

    """Este metodo es un wrapper que abre una curva, la preprocesa,
    saca muestras con un GP y después las guarda en algún lugar.
    """

    try:
        lc = lu.open_lightcurve(lc_path, catalog=catalog)
        lc = lu.filter_data(lc)

        if lc_sampling == 'normal':
            lc = lc.iloc[0:int(percentage * lc.index.size)]
        elif lc_sampling == 'new':
            lc = lc.iloc[np.linspace(0, lc.index.size,
                                     num=int(percentage * lc.index.size),
                                     dtype=int)]

        t_obs, y_obs, err_obs, min_time, max_time = lu.prepare_lightcurve(lc)

        var = np.var(y_obs)
        l = 6
        kernel = var * kernels.ExpSquaredKernel(l ** 2)

        if param_choice == 'fitted':
            kernel = optimize.find_best_fit(kernel, t_obs, y_obs, err_obs)
            kernel = kernel + kernels.WhiteKernel(np.var(err_obs))

        samples_devs = bootstrap.GP_bootstrap(lc, kernel, sampling, n_samples)
        result_dir = (samples_path +
                      lu.get_lightcurve_class(lc_path, catalog=catalog) + '/' +
                      lu.get_lightcurve_id(lc_path, catalog=catalog) + ' samples.pkl')

        output = open(result_dir, 'wb')
        cPickle.dump(samples_devs, output)
        output.close()

    except Exception as e:
        print e
        err_path = (samples_path + 'error.txt')
        f = open(err_path, 'a')
        f.write(lc_path + '\n')
        f.close()

if __name__ == '__main__':

    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Get bootstrap samples from lightcurves')
    parser.add_argument('--percentage', required=True, type=str)
    parser.add_argument('--n_samples', required=True, type=int)
    parser.add_argument('--n_processes', required=True, type=int)
    parser.add_argument('--sampling', required=True, type=str)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS'])
    parser.add_argument('--lc_filter', required=False, type=float, 
                        help='Percentage of the total amount of paths to use')
    parser.add_argument('--param_choice', required=True, type=str)
    parser.add_argument('--samples_path', required=True, type=str)

    args = parser.parse_args(sys.argv[1:])

    percentage = int(args.percentage) / float(100)
    catalog = args.catalog
    sampling = args.sampling
    n_samples = args.n_samples
    n_processes = args.n_processes
    lc_filter = args.lc_filter
    param_choice = args.param_choice
    samples_path = args.samples_path


    # Creo archivo para guardar errores
    if os.path.isfile(samples_path + 'error.txt'):
        os.remove(samples_path + 'error.txt')

    paths = lu.get_lightcurve_paths(catalog=catalog)

    if lc_filter is not None:
        paths = lu.stratified_filter(paths, catalog=catalog, percentage=lc_filter)
    print 'Analisis sobre ' + str(len(paths)) + ' curvas'

    # Filtro ids de curvas ya calculadas
    ids = lu.get_ids_in_path(samples_path, catalog=catalog, extension='.pkl')
    paths = [x for x in paths if lu.get_lightcurve_id(x, catalog=catalog) not in ids]

    partial_sample = partial(sample_curve, catalog=catalog,
                             percentage=percentage, sampling=sampling,
                             n_samples=n_samples, param_choice=param_choice,
                             samples_path=samples_path)

    pool = multiprocessing.Pool(processes=n_processes)
    pool.map(partial_sample, paths)

    pool.close()
    pool.join()
