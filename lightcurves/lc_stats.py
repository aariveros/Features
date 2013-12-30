from __future__ import division
import lc_IO as io
import numpy as np
import pandas as pd
import lc_utils as lu
import os
import re


def normalize( d, minimo, maximo, new_min=0, new_max=1 ):
    if(maximo == minimo):
        return d * (new_max - new_min) + new_min
    else:
        return (float(d - minimo) / (maximo - minimo)) * (new_max - new_min) + new_min

"""
 Retorna el valor de una feature calculada con la curva cortada hasta distintos
 porcentajes. Y el porcentaje de completitud de la curva.

 percentage: si se especifica un porcentaje, solo se calculan las features
 hasta ese porcentaje de puntos
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
    x_values = []
    y_values = []

    steps = int(len(lc.index) / percentage) - 2

    for i in range(3, steps):
        y_values.append( feature( lc.iloc[0:i*percentage]) )
        
        aux = float(i*percentage)/len(lc.index)
        # x_values.append( aux )
        print('Progress: ' + '{0:.2f}'.format(aux*100) + '%')    

        x_values.append(i*percentage)
        
    x_values.append(len(lc.index))
    y_values.append(feature(lc))
    
    completitud = []
    for i in range(2, len(y_values)):
        completitud.append(comp(y_values[0:i]))

    return x_values, y_values, completitud

# def get_feat_and_comp(lc, feature, percentage=1):
#     progress, feature_values = feature_progess( lc, feature )

#     completitud = []
#     for i in range(2, len(feature_values)):
#         completitud.append( var_completeness(feature_values[0:i]))

#     return progress, feature_values, completitud


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
        variaciones.append( abs(y_values[i] - y_values[i-1]))

    max_var = max(variaciones)
    min_var = 0
    # min_var = min(variaciones)

    prom_var = sum(variaciones) / (n - 1)

    # print( 'Maxima varianza: ' + str(max_var))
    # print( 'Minima varianza: ' + str(min_var))
    # print( 'Promedio de varianza. ' + str(aux))
    return 1 - normalize( prom_Var, min_var, max_var)   

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
    
    return 1 - normalize( varianza, min_var, max_var)

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

    return 1 - normalize(prom_var, min_var, max_var)

"""
 Toma el path a un archivo de features de una estrella en particular y retorna
 
"""

def get_comp(path):
    pass

"""
 Toma el path de un directorio con los archivos del progreso de las features de estrellas
 y genera un unico archivo para usar como base de entrenamiento.
"""

RESULTS_DIR_PATH = '/Users/npcastro/workspace/Features/Entrenamiento/'

def get_training_set(path):

    # Abro el directorio y obtengo el nombre de todos los archivos
    archivos = []
    for dirpath,_,filenames in os.walk(path):
       for f in filenames:
            if '.txt' in f:
                archivos.append(os.path.abspath(os.path.join(dirpath, f)))

    
    # Obtengo el header con las features de los datos
    with open(archivos[0], 'r') as f:
        header = f.readline().strip()

    f.close()

    # Agrego los comp al header
    aux = []
    for f in header.split(' '):
        if f != '#Punto':
            aux.append(f)
            aux.append(f + '_comp')
    header = ' '.join(aux)

    # Agrego el label y el macho_id
    header = '#Macho_id ' + header + ' label'

    # print header

    # io.init_results_file(header, [20])

    # Lista de lineas a escribir en el archivo final
    lineas = []
    lineas.append(header)

    # Para cada archivo
    for a in archivos:

        linea = []

        # Agrego el macho_id de la curva
        linea.append(lu.get_lightcurve_id(a))

        # Armo un dataframe con los valores de las features en el tiempo
        df = pd.read_csv(a, sep=" ", index_col=0)

        # Para cada feature 
        for c in df.columns:
            serie = df[c]

            # Obtengo el porcentaje de la curva que voy a considerar
            total = len(serie.index)
            parcial = int(total*20/100)

            # calculo su completitud y guardo el valor de la feature en el mismo punto
            valor_feature = serie.iloc[parcial]
            confianza = var_completeness(serie[0:parcial].tolist())
            linea.append(str(valor_feature))
            linea.append(str(confianza))

        # Obtengo el label
        linea.append(str(lu.get_lc_class(a)))

        lineas.append(' '.join(linea))

        # print lineas

    # Escribo el archivo de respuestas
    with open('Resultados 20.txt', 'w') as f:
        print lineas
        for linea in lineas:
            f.write(linea + '\n')
    f.close()
