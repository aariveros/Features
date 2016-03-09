# coding=utf-8

# Le ajusta un GP a un set de curvas y guarda los valores medios del modelo
# para los ptos donde hay observaciones
# -----------------------------------------------------------------------------

import os
import sys
import argparse
import multiprocessing
from functools import partial

import bootstrap
from config import *
import lightcurves.lc_utils as lu


if __name__ == '__main__':

    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Get bootstrap samples from lightcurves')
    parser.add_argument('--percentage', required=True, type=str)
    parser.add_argument('--n_processes', required=True, type=int)
    parser.add_argument('--sampling', required=True, type=str)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS'])
    parser.add_argument('--lc_filter', required=False, type=float, 
                        help='Percentage of the total amount of paths to use')
    parser.add_argument('--param_choice', required=True, type=str)
    parser.add_argument('--result_dir', required=True, type=str)

    args = parser.parse_args(sys.argv[1:])

    percentage = int(args.percentage) / float(100)
    catalog = args.catalog
    sampling = args.sampling
    n_processes = args.n_processes
    lc_filter = args.lc_filter
    param_choice = args.param_choice
    result_dir = args.result_dir


    # Creo archivo para guardar errores
    if os.path.isfile(samples_path + 'error.txt'):
        os.remove(samples_path + 'error.txt')

    paths = lu.get_lightcurve_paths(catalog=catalog)

    if lc_filter is not None:
        paths = lu.stratified_filter(paths, percentage=lc_filter)
    print 'Analisis sobre ' + str(len(paths)) + ' curvas'

    # Filtro ids de curvas ya calculadas
    ids = lu.get_ids_in_path(result_dir, catalog=catalog, extension='.pkl')
    paths = [x for x in paths if lu.get_lightcurve_id(x, catalog=catalog) not in ids]

    partial_sample = partial(bootstrap.GP_sample_mean, catalog=catalog,
    						 percentage=percentage, sampling=sampling,
                             param_choice=param_choice, result_dir=result_dir)

    pool = multiprocessing.Pool(processes=n_jobs)
    pool.map(partial_sample, paths)

    pool.close()
    pool.join()
