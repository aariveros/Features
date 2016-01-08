# coding=utf-8
# Archivo con métodos generales que ocupo repetidamente en mi codigo

# -----------------------------------------------------------------------------

import os

def get_paths(directory, extension=''):
    """Entrega todos los paths absolutos a objetos de distintos tipos en un
    directorio
    """
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if extension in f:
               	yield(os.path.abspath(os.path.join(dirpath, f)))