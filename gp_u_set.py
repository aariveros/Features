# coding=utf-8

# Toma un directorio con archivos de features sampleadas de curvas de luz
# Para cada set de features sampleadas calcula las gaussianas asociada a cada
# variable. Le agrega la clase y un peso con valor 1 y arma un dataframe y lo
# guarda como set de entrenamiento

# --------------------------------------------------------------------------
import pandas as pd
import os
import lightcurves.lc_utils as lu

def get_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


output_file_name = 'gp_u_set_60.csv'

feature_names = ['Amplitude', 'Beyond1Std', 'Con', 'MaxSlope', 'MedianAbsDev', 'MedianBRP', 'PairSlopeTrend', 'Rcs', 'Skew', 'SmallKurtosis', 'Std', 'StestonK', 'VariabilityIndex', 'meanvariance']

linea = []
for name in feature_names:
    linea.append(name+'.l')
    linea.append(name+'.mean')
    linea.append(name+'.r')
    linea.append(name+'.std')
linea.append('weight')
linea.append('class')
linea = ','.join(linea) + '\n'
f = open(output_file_name, 'w')
f.write(linea)
f.close()

path = '/Users/npcastro/workspace/Features/GP Samples/60'
files = get_paths(path)

lineas = []

for f in files:
    # print f
    if '.DS_Store' in f or 'error.txt' in f or 'pocos_puntos.txt' in f:
        continue

    df = pd.read_csv(f)

    medias = df.mean()
    std = df.std()
    l = medias - 3*std
    r = medias + 3*std

    medias = medias.tolist()
    std = std.tolist()
    l = l.tolist()
    r = r.tolist()

    linea = []
    for i in xrange(len(medias)):
        linea.append(str(l[i]))
        linea.append(str(medias[i]))
        linea.append(str(r[i]))
        linea.append(str(std[i]))

    linea.append('1.0')
    linea.append(lu.get_lc_class_name(f))

    lineas.append(','.join(linea) + '\n')

f = open(output_file_name, 'a')
f.writelines(lineas)
f.close()

