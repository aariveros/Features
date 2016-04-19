# coding=utf-8
# Tomo los archivos con valores de features sampleadas para cada curva. Tomo N
# muestras para cada curva y las junto en un solo dataset mas grande

# -----------------------------------------------------------------------------

import sys
import argparse

import pandas as pd

import lightcurves.lc_utils as lu

if __name__ == '__main__':

    # Recibo parámetros de la linea de comandos
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser(
        description='Calc features to lightcurves and form dataset')
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS'])
    parser.add_argument('--n_samples', required=True, type=int)
    parser.add_argument('--samples_path', required=True, type=str)
    parser.add_argument('--result_file', required=True, type=str)
    
    args = parser.parse_args(sys.argv[1:])

    catalog = args.catalog
    n_samples = args.n_samples
    samples_path = args.samples_path
    result_file = args.result_file
    
    paths = lu.get_paths(samples_path, '.csv')
    paths = [x for x in paths]

    feature_list = ['']
    feature_list.extend(pd.read_csv(paths[0]).columns.tolist())
    feature_list.append('class')
    linea = ','.join(feature_list) + '\n'

    f = open(result_file, 'w')
    f.write(linea)

    for path in paths:
        lineas = []
        df = pd.read_csv(path)
        lc_id = lu.get_lightcurve_id(path, catalog=catalog)
        lc_class = lu.get_lightcurve_class(path, catalog=catalog)

        for i in xrange(n_samples):
            linea = [lc_id]
            linea.extend(map(str, df.iloc[i].tolist()))
            linea.append(lc_class)
            linea = ','.join(linea) + '\n'
            lineas.append(linea)

        f.writelines(lineas)

    f.close()
