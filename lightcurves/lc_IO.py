from __future__ import division
import matplotlib.pyplot as plt
import numpy as np

from lc_utils import *
from lc_stats import *

from config import *

import os

def add_names( title, x_name, y_name):
    if title:
        plt.title(title) 

    if x_name:
        plt.xlabel(x_name)

    if y_name:
        plt.ylabel(y_name, rotation = 'horizontal', labelpad=20)

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
    """ Guarda la evolucion de las features de una curva en un .txt

    Parameters 
    ----------

    path: Nombre del archivo de la curva de luz.
    header: String con el nombre de las features calculadas
    puntos: Indice de los puntos para los que fueron calculadas las features
    feat_values: Valores de las distintas features

    """
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


def graf_feature( x_values, y_values, title, comp_x_values, comp_y_values, num_graf ):
    """
    x_value: Eje x, porcentajes de completitud de la curva para los que se calcula la feature
    y_value: Valor de la feature para cada porcentaje de puntos usados
    title: Titulo del grafico
    comp_x_values: Eje x para el indice de completitud de la feature
    comp_y_values: Valores del indice de completitud
    num_graf: Numero del grafico

    """

    #### Curva superior del grafico ####

    # Creo y grafico la figura
    plt.figure(num_graf)
    plt.subplot(211)
    plt.plot( x_values,y_values, '.')
    # plt.axhline(y = y_values[-1], color = 'r')

    add_names(title=title, x_name=None, y_name=Brillo)

    # plt.xlim(0.0, 1.0)
    plt.xlim(x_values[0], x_values[len(x_values)-1])
    
    # Otros
    ax = plt.gca()
    ax.xaxis.grid(True)
    ax.yaxis.labelpad = 8

    #### Curva inferior del grafico ####

    # Creo y grafico
    plt.subplot(212)
    plt.plot( comp_x_values, comp_y_values, '.')
    plt.axhline(y = comp_y_values[-1], color = 'r')

    add_names(x_name='Porcentaje de curva', y_name='Valor descriptor')

    plt.xlim(0.0, 1.0)
    plt.xlim(x_values[0], x_values[len(x_values)-1])
    
    # Guardo y/o muestro
    # plt.savefig(title+'.png')
    plt.show()
    plt.close()

def graf_feature_progress( y_values, title ):
    plt.figure()

    total_points = len(y_values)
    x_values = [ float(i) / total_points for i in xrange(total_points) ]

    plt.plot( x_values, y_values, '.')
    plt.axhline(y = y_values[-1], color = 'r')

    add_names(title, 'Curve percentage', 'Feature Value')

    plt.xlim(0.0, 1.0)
    # plt.ylim(0.0, 1.0)

    #plt.xlim(x_values[0], x_values[len(x_values)-1])

    # Guardo y/o muestro
    plt.savefig(RESULTS_DIR_PATH + title + '.png')
    #plt.show()
    plt.close()

def graf_lc_and_feature_progress( x_values, mag_values, feat_values, macho_id, class_name, feat_name ):
    """Genera un grafico con la curva de luz en la parte superior, y con la evolucion de un descriptor en la parte inferior.

    Parameters
    ----------
    x_values: list(float)
        tiempos en que fueron medidos los puntos de la curva
    mag_values: list(float)
        valores de la curva de luz en el tiempo
    feat_values: list(float)
        valores de la feature en el tiempo
    title: string
        titulo del grafico. 
    class_name: string 
        nombre de la clase de estrella que se esta graficando. (Necesario para crear el directorio y guardarlo)
    feat_name: string
        nombre de la feature que se esta graficando
    """

    mag_values = normalize_z(mag_values)
    feat_values = normalize_z(feat_values)

    plt.figure()
    plt.subplot(211)

    ###### Grafico curva de luz en la parte superior del grafico #######
    plt.plot( x_values, mag_values, '.')

    add_names(macho_id + ' ' + feat_name, "MJD", 'Mag')
    
    # Dimensiones
    plt.xlim(x_values[0], x_values[-1])
    # plt.ylim(-2, -10)
    
    # Otros
    ax = plt.gca()
    ax.xaxis.grid(True)
    ax.yaxis.labelpad = 8

    ###### Feature ######
    plt.subplot(212)

    total_points = len(feat_values)
    x_values = [ float(i) / total_points for i in xrange(total_points) ]

    plt.plot( x_values, feat_values, '.')
    plt.axhline(y = feat_values[-1], color = 'r')

    add_names(x_name='Curve percentage', y_name='Feature')
     
    plt.ylim(-7.0, 7.0)
    plt.xlim(0.0, 1.0)

    #plt.xlim(x_values[0], x_values[len(x_values)-1])

    # Guardo y/o muestro
    save(RESULTS_DIR_PATH + class_name + '/' + feat_name + '/' + macho_id + '.png')

def graf_lc_and_feature_progress_unnormalized( x_values, mag_values, feat_values, macho_id, class_name, feat_name ):
    """Genera un grafico  de tres partes curva de luz, evolucion de feature normalizada y sin normalizar.

    Parameters
    ----------
    x_values: list(float)
        tiempos en que fueron medidos los puntos de la curva
    mag_values: list(float)
        valores de la curva de luz en el tiempo
    feat_values: list(float)
        valores de la feature en el tiempo
    title: string
        titulo del grafico. 
    class_name: string 
        nombre de la clase de estrella que se esta graficando. (Necesario para crear el directorio y guardarlo)
    feat_name: string
        nombre de la feature que se esta graficando
    """

    mag_values = normalize_z(mag_values)

    plt.figure()
    plt.subplot(311)

    ###### Grafico curva de luz en la parte superior del grafico #######
    plt.plot( x_values, mag_values, '.')

    # Labels
    plt.title(macho_id + ' ' + feat_name)
    plt.ylabel( 'Mag', rotation = 'horizontal', horizontalalignment = 'right')
    plt.xlabel( "MJD")
    
    # Dimensiones
    plt.xlim(x_values[0], x_values[-1])
    # plt.ylim(-2, -10)
    
    # Otros
    ax = plt.gca()
    ax.xaxis.grid(True)
    ax.yaxis.labelpad = 8

    ###### Feature normalizada ######
    plt.subplot(312)

    normed_feat_values = normalize_z(feat_values)

    total_points = len(normed_feat_values)
    x_values = [ float(i) / total_points for i in xrange(total_points) ]

    plt.plot( x_values, normed_feat_values, '.')
    plt.axhline(y = normed_feat_values[-1], color = 'r')

    # Labels
    plt.ylabel( 'Feature', rotation = 'horizontal', horizontalalignment = 'right' )
    plt.ylim(-7.0, 7.0)

    plt.xlabel( 'Curve percentage')    
    plt.xlim(0.0, 1.0)

    ###### Feature sin normalizar ######
    plt.subplot(313)

    total_points = len(feat_values)
    x_values = [ float(i) / total_points for i in xrange(total_points) ]

    plt.plot( x_values, feat_values, '.')
    plt.axhline(y = feat_values[-1], color = 'r')

    # Labels
    plt.ylabel( 'Feature', rotation = 'horizontal', horizontalalignment = 'right' )

    plt.xlabel( 'Curve percentage')    
    plt.xlim(0.0, 1.0)

    # Guardo y/o muestro
    save(RESULTS_DIR_PATH + class_name + '/' + feat_name + '/' + macho_id + '.png')


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

def save(path):
    """Save a figure from pyplot.
 
    Parameters
    ----------
    path : string
        The path (and filename) to save the
        figure to.
    """
    
    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    filename = os.path.split(path)[1]
    if directory == '':
        directory = '.'
 
    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)
 
    # The final path to save to
    savepath = os.path.join(directory, filename)
 
    # Actually save the figure
    plt.savefig(savepath)
    plt.close()

def graf_gp_fit(X, y, x_pred, y_pred, sigma):
    """Graf an adjusted gaussian process model over a set of points.
    
    parameters
    ----------
    X: puntos de las observaciones
    y: valor de f(x) en las observaciones
    x_pred: puntos donde se pregunta al gp
    y_pred: f(x) dde se pregunto al gp
    sigma: std en los ptos dde se pregunto al modelo
    
    """
    # Grafico las observaciones
    X2 = np.array(X)
    X2 = (X2.T).ravel()
    plt.plot(X2,y,'.r')
    
    # Grafico la regresion ajustada
    X3 = np.array(x_pred)
    X3 = X3.ravel()
    plt.plot(X3, y_pred, 'b-', label=u'Prediction')
    
    # Agrego el intervalo de confianza
    plt.fill(np.concatenate([X3, X3[::-1]]), \
            np.concatenate([y_pred - 1.9600 * sigma,
                           (y_pred + 1.9600 * sigma)[::-1]]), \
            alpha=.5, fc='#C0C0C0', ec='None', label='95% confidence interval')
    
    # Leyenda
    plt.xlabel('$x$')
    plt.ylabel('$f(x)$')
    plt.legend(loc='upper right')