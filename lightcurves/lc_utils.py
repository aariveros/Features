from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

LC_FILE_PATH = '/Users/npcastro/workspace/Features/lightcurves_paths/Todas.txt'
RESULTS_DIR_PATH = '/Users/npcastro/workspace/Features/Resultados/'


"""
fp: Absolute file path of the lightcurve file
"""
def open_lightcurve(fp):
    cols = ['mjd', 'mag', 'err']
    data = pd.read_table(fp, skiprows = [0,1,2], names = cols,
            index_col = 'mjd', sep = '\s+')
    return data

"""
lc_list: iterable with lightcurve file paths
returns: list with Pandas DataFrames for each lightcurve
"""
def open_lightcurves(lc_list):
    return map(open_lightcurve, lc_list)

"""
return val: file object with lightcurve paths in each line
"""
def get_lightcurve_paths(path=LC_FILE_PATH, separate_bands=False):
    f = open(path, 'r')

    if separate_bands:
        azules = [l[:-1] for l in f if '.B.mjd' in l]
        f.seek(0)
        rojas = [l[:-1] for l in f if '.R.mjd' in l]
        return azules, rojas
    else:   
        return [l[:-1] for l in f]

"""
return val: string containing de macho_id of the curve
"""
def get_lightcurve_id(fp):
    pattern = re.compile('[0-9]*\.[0-9]*\.[0-9]*')
    return pattern.search(fp).group()

"""
fp: lightcurve file path
return val: class as an integer
"""
def get_lc_class(fp):
    if "Be_lc" in fp:
        return 2
    elif "CEPH" in fp:
        return 3
    elif "EB" in fp:
        return 4
    elif "longperiod_lc" in fp:
        return 5
    elif "microlensing_lc" in fp:
        return 6
    elif "non_variables" in fp:
        return 7
    elif "quasar_lc" in fp:
        return 8
    elif "RRL" in fp:
        return 9
    return 0

"""
 Retorna el nombre de la clase de la estrella
"""

def get_lc_name(fp):
    # /Users/npcastro/Dropbox/Tesis/lightcurves/Be_lc/lc_1.3567.1310.B.mjd
    pattern = re.compile('lightcurves/.*/')
    return pattern.search(fp).group().split('/')[1]

"""
fp: lightcurve file path
return val: band as a string
"""
def get_lc_band(fp):
    if ".R.mjd" in fp:
        return "R"
    elif ".B.mjd" in fp:
        return "B"


"""
 Recibe una curva de luz, y la retorna eliminando todos los puntos
 que se encuentran fuera de una cantidad errores promedio
 lc: dataframe de la curva de luz
 rango: rango de filtro, default 3 medias del error
 norm: si es true la curva se centra en 0, default false
"""
def filter_data( lc, rango = 3, norm = False ):

    [magnitud_media, error_medio] = lc.mean( axis = 0)

    lc = lc[lc['err'] < rango * error_medio]

    if norm:
        pass

    return lc

"""
 Retorna el valor de una feature calculada con la curva cortada hasta distintos
 porcentajes. Y el porcentaje de completitud de la curva.

 percentage: si se especifica un porcentaje, ese porcenaje de veces 
 la feature 
"""

def feature_progress( lc, feature, percentage=1 ):
    x_values = []
    y_values = []

    steps = int(len(lc.index) / percentage) - 2

    for i in range(3, steps):
        y_values.append(feature( lc.iloc[0:i*percentage]) )
        
        aux = float(i*percentage)/len(lc.index)
        # x_values.append( aux )
        print('Progress: ' + '{0:.2f}'.format(aux*100) + '%')    

        x_values.append(i*percentage)

    x_values.append(len(lc.index))
    y_values.append(feature(lc))

    return x_values, y_values

"""
 Retorna los valores de una feature calculada progresivamente a medida que se completa
 la curva. Ademas retorna la confianza en la feature a medida que esta avanza

 percentage:    Fraccion de puntos de la curva para los que se calculara la feature. Sirve
                para acelerar el calculo de features mas lentas. 

"""

def get_feat_and_comp(lc, feature, comp, percentage=1):
    x_values, y_values = feature_progress(lc, feature, percentage)
    
    completitud = []
    for i in range(2, len(y_values)):
        completitud.append(comp(y_values[0:i]))

    return x_values, y_values, completitud


"""
 Retorna el grado de confianza de una feature incompleta.
 Retorna 1 -  el promedio de las diferencias entre cada punto y
 el antecesor. Considera max_var como la maxima diferencia presente, 
 entre un punto y el siguiente (en valor absoluto) en la curva de luz. 
"""

def completeness( y_values ):
    variaciones = []
    n = len(y_values)

    for i in range(1, n):
        variaciones.append(abs(y_values[i] - y_values[i-1]))

    max_var = max(variaciones)
    min_var = 0
    # min_var = min(variaciones)

    prom_var = sum(variaciones) / (n - 1)

    # print( 'Maxima varianza: ' + str(max_var))
    # print( 'Minima varianza: ' + str(min_var))
    # print( 'Promedio de varianza. ' + str(aux))
    return prom_var
    #return 1 - normalize( prom_var, min_var, max_var)

"""
 Retorna el grado de confianza de una feature incompleta.   
 Retorna 1 - la varianza de los datos, normalizada entre 0 y max_var.
 Considera max_var como la maxima diferencia con la media de los datos.
"""

def var_completeness( y_values ):
    n = len(y_values)
    media = np.mean( y_values )
    variaciones = []

    max_var = 0
    min_var = 0

    for i in range(len(y_values)):
        aux = (y_values[i] - media)**2

        if( aux > max_var):
            max_var = aux

        variaciones.append(aux)

    varianza = sum(variaciones) / (n-1)
    
    return varianza
    #return 1 - normalize( varianza, min_var, max_var)

"""
 Calcula la confianza de una feature incompleta. 
 Retorna 1 - el promedio de las diferencias entre cada punto y
 el ultimo valor de la feature. Considera max_var como la maxima diferencia presente, 
 entre un punto y el ultimo valor de la feature en la curva de luz.

"""
def trust( y_values ):
    n = len(y_values)
    final = y_values[-1]

    variaciones = []
    max_var = 0
    min_var = 0

    for i in range(len(y_values)):
        aux = abs(y_values[i] - final)

        if(aux > max_var):
            max_var = aux
        variaciones.append(aux)

    prom_var = sum(variaciones) / (n - 1)

    return prom_var
    #return 1 - normalize(prom_var, min_var, max_var)


"""
 Retorna el grado de completitud de una feature para cada cantidad de puntos 
 posibles
"""

def completition_progress( y_values ):
    pass


def normalize( d, minimo, maximo, new_min=0, new_max=1 ):
    if(maximo == minimo):
        return d * (new_max - new_min) + new_min
    else:
        return (float(d - minimo) / (maximo - minimo)) * (new_max - new_min) + new_min