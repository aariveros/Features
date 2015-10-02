# coding=utf-8  

import pandas as pd
import shutil

import os
import re

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
                if '.time' in f and label in f:
                    archivo.write(f + '\n')
    else:
        with open('lightcurves_paths/EROS.txt', 'w') as archivo:
            for f in files:
                if '.time' in f:
                    archivo.write(f + '\n')

def get_id(path):
    """Recibe un path absoluto a un archivo de una curva de luz de EROS y 
    retorna el id de la curva
    """
    pattern = re.compile('lm.*[^.time]')
    return pattern.search(path).group()
    

if __name__ == '__main__':

    writePathsFile('/n/seasfs03/IACS/TSC/ncastro/EROS')

    class_dict = {0: "Ceph_10",
                  1: "Ceph_10_20",
                  2: "Ceph_F",
                  3: "EB",
                  4: "LPV",
                  5: "Mira_AGB_O",
                  6: "OSARG_RGB_O",
                  7: "SRV_AGB_C",
                  8: "SRV_AGB_O",
                  9: "RRL",
                  10: "T2CEPH"
    }

    #lc_files = absoluteFilePaths('/Users/npcastro/Desktop/EROS/EROS')
    #classes_df = pd.read_csv('/Users/npcastro/Desktop/EROS/karim_classes.csv', index_col=0)

    #error_count = 0
    #for path in lc_files:
    #    if '.time' in path:
    #        try:
    #            lc_id = get_id(path)
    #            clase = class_dict[classes_df.loc[lc_id]['class']]
    #            shutil.copy(path, '/Users/npcastro/Dropbox/EROS/' + clase + '/' + lc_id + '.time')
    #        except KeyError:
    #            print lc_id
    #            error_count += 1

        
