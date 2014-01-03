from __future__ import division
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lc_utils import *

RESULTS_DIR_PATH = '/Users/npcastro/workspace/Features/Resultados/'

def save_line(linea, p):
    with open(RESULTS_DIR_PATH + 'Resultados {0}.txt'.format(p), 'a') as f:
        f.write(linea + '\n')
        f.close()

def init_results_file(header, porcentajes = [20, 40, 60, 80, 100]):    
    for p in porcentajes:
        f = open(RESULTS_DIR_PATH + 'Resultados {0}.txt'.format(p), 'w')
        f.write(header)
        f.close()

def save_lc(path, header, puntos, feat_values):
    macho_id = get_lightcurve_id(path)
    class_name = get_lc_name(path)

    with open(RESULTS_DIR_PATH + class_name + '/' + macho_id + '.txt', 'w') as archivo:
        
        archivo.write(header)
        for i in range(len(puntos)):
            linea = str(puntos[i])
            for f in feat_values:
                linea = linea + ' ' + str(f[i])

            linea = linea.strip()
            
            archivo.write(linea + '\n')

"""
x_value: Eje x, porcentajes de completitud de la curva para los que se calcula la feature
y_value: Valor de la feature para cada porcentaje de puntos usados
title: Titulo del grafico
comp_x_values: Eje x para el indice de completitud de la feature
comp_y_values: Valores del indice de completitud
num_graf: Numero del grafico

"""
def graf_feature( x_values, y_values, title, comp_x_values, comp_y_values, num_graf ):
    plt.figure(num_graf)
    plt.subplot(211)
    plt.plot( x_values,y_values, '.')
    plt.axhline(y = y_values[-1], color = 'r')
    plt.title( title)
    plt.ylabel( 'Feature Value' )
    plt.xlabel( "% of points")
    # plt.xlim(0.0, 1.0)
    plt.xlim(x_values[0], x_values[len(x_values)-1])
    ax = plt.gca()
    ax.xaxis.grid(True)

    plt.subplot(212)
    plt.plot( comp_x_values, comp_y_values, '.')
    plt.xlabel( 'Porcentaje de curva')
    # plt.xlim(0.0, 1.0)
    plt.xlim(x_values[0], x_values[len(x_values)-1])
    plt.ylabel( 'Completitud' )
    plt.ylim(0.0, 1.0)
    # plt.savefig(title+'.png')
    
    plt.show()
    plt.close()

def graf_lc( x_values, y_values, title, percentage = 1):
    plt.figure(1)
    indice = int(len(x_values)*percentage)

    plt.plot( x_values[0:indice], y_values[0:indice], 'bo')
    plt.xlim(0.0, 1.0)
    plt.ylim(-8.6, -8.0)
    plt.title(title)

    plt.xlabel( 'Porcentaje de curva')
    plt.ylabel( 'Magnitud' )
    # plt.show()
    plt.savefig(str(percentage*100) + '.png')