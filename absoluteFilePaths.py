import os
from config import *

"""
Hace una busqueda recursiva por todos los directorios del directorio recibido. Y retorna una lista
con el path absoluto de todos los archivos que encuentra

"""
def absoluteFilePaths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


"""
 Recibe un directorio, busca recursivamente los archivos en busqueda de estrellas
 y escribe sus paths absolutos en un archivo.

 class: Si se le entrega un string de clase. Va a buscar esa extension en los archivos
 y solo escribira esos paths en un archivo con el nombre de la clase.
"""


def writePathsFile(dir, label=None):
    files = absoluteFilePaths(dir)

    if label:
        with open(label + '.txt', 'w') as archivo:
            for f in files:
                if '.mjd' in f and label in f:
                    archivo.write(f + '\n')
    else:
        with open('lightcurves_paths/paths.txt', 'w') as archivo:
            for f in files:
                if '.mjd' in f:
                    archivo.write(f + '\n')


if __name__ == '__main__':
    dir = LC_PATH
    # Para todas los paths en un solo archivo
    writePathsFile(dir)

    # Para elegir un clase particular por archivo

    # writePathsFile(dir, 'Be_lc')
    # writePathsFile(dir, 'CEPH')
    # writePathsFile(dir, 'EB')
    # writePathsFile(dir, 'longperiod_lc')
    # writePathsFile(dir, 'microlensing_lc')
    # writePathsFile(dir, 'non_variables')
    # writePathsFile(dir, 'quasar_lc')
    # writePathsFile(dir, 'RRL')
