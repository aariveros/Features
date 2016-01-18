# coding=utf-8
# Tomo los archivos con valores de features sampleadas para cada curva. Tomo N
# muestras para cada curva y las junto en un solo dataset mas grande

# -----------------------------------------------------------------------------

import pandas as pd

import sys

import lightcurves.lc_utils as lu

N = 10
percentage = sys.argv[1]
directory = '/n/seasfs03/IACS/TSC/ncastro/Samples_Features/MACHO/' + percentage + '%/'
paths = lu.get_paths(directory, '.csv')
paths = [x for x in paths]

result_file = '/n/seasfs03/IACS/TSC/ncastro/sets/MACHO_Big/macho big ' + percentage + '.csv'

feature_list = ['']
feature_list.extend(pd.read_csv(paths[0]).columns.tolist())
feature_list.append('class')
linea = ','.join(feature_list) + '\n'

f = open(result_file, 'w')
f.write(linea)

for path in paths:
    lineas = []
    df = pd.read_csv(path)
    lc_id = lu.get_lightcurve_id(path, catalog='MACHO')
    lc_class = lu.get_lightcurve_class(path, catalog='MACHO')

    for i in xrange(N):
        linea = [lc_id]
        linea.extend(map(str, df.iloc[i].tolist()))
        linea.append(lc_class)
        linea = ','.join(linea) + '\n'
        lineas.append(linea)

    f.writelines(lineas)

f.close()
