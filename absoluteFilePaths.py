# coding=utf-8

# Me todos para generar archivos con el path absoluto a un conjunto de curvas
# de luz
# -----------------------------------------------------------------------------

import os
from config import *

def absoluteFilePaths(directory):
    """Hace una busqueda recursiva por todos los directorios del directorio
    recibido. Y retorna una lista con el path absoluto de todos los archivos
    que encuentra.
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def writePathsFile(dir, label=None):
    """Busca recursivamente los archivos de  estrellas en un directorio y 
    escribe sus paths absolutos en un archivo.

    label: Si se le entrega un string de clase. Solo considera los archivos
    con esa extensión
    """
    files = absoluteFilePaths(dir)

    if label:
        with open(label + '.txt', 'w') as archivo:
            for f in files:
                if '.mjd' in f and label in f:
                    archivo.write(f + '\n')
    else:
        with open('lightcurves_paths/Todas.txt', 'w') as archivo:
            for f in files:
                if '.mjd' in f:
                    archivo.write(f + '\n')


if __name__ == '__main__':
    dir = LC_PATH
    # Para todas los paths en un solo archivo
    # writePathsFile(dir)

    # Para elegir un clase particular por archivo

    writePathsFile(dir, 'Be_lc')
    writePathsFile(dir, 'CEPH')
    writePathsFile(dir, 'EB')
    writePathsFile(dir, 'longperiod_lc')
    writePathsFile(dir, 'microlensing_lc')
    writePathsFile(dir, 'non_variables')
    writePathsFile(dir, 'quasar_lc')
    writePathsFile(dir, 'RRL')
