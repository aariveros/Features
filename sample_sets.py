# coding=utf-8

# Toma un directorio con archivos de features sampleadas de curvas de luz.
# Con ellos separo los valores de las features en n sets de entrenamiento
# distintos. Donde n es el numero de muestras

# -----------------------------------------------------------------------------
import sys
import argparse

import pandas as pd

import lightcurves.lc_utils as lu
from config import *

if __name__ == '__main__':

    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('--percentage', required=True, type=str)
    parser.add_argument('--catalog', default='MACHO',
                        choices=['MACHO', 'EROS', 'OGLE'])
    parser.add_argument('--sampling', required=True, type=str)

    args = parser.parse_args(sys.argv[1:])

    percentage = args.percentage
    catalog = args.catalog
    sampling = args.sampling
    result_file_path = args.result_file_path

    samples_path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%/'

    feature_samples_files = lu.get_paths(samples_path, '.csv')
    feature_samples_files = [x for x in feature_samples_files]
    ids = [lu.get_lightcurve_id(x, catalog=catalog) for x in feature_samples_files]

    feature_list = ['']
    feature_list.extend(pd.read_csv(feature_samples_files[0]).columns.tolist())
    feature_list.append('class')
    linea = ','.join(feature_list) + '\n'

    archivos = []
    for i in xrange(100):       # El 100 esta harcodeao
        f = open(result_file_path + 'macho_sampled_' + str(i) + '.csv', 'w')
        f.write(linea)
        archivos.append(f)
    
    for f in feature_samples_files:
        lc_id = lu.get_lightcurve_id(f)
        lc_class = lu.get_lightcurve_class(f, catalog=catalog)

        archivo = open(f, 'r')

        # Boto la primera linea con el nombre de las columnas
        archivo.readline()

        for index, l in enumerate(archivo):
            linea = [lc_id]
            linea.extend(l.strip('\n').split(','))
            linea.append(lc_class)
            linea = ','.join(linea) + '\n'

            archivos[index].write(linea)
    
    for f in archivos:
        f.close()
