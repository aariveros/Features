# coding=utf-8

# Script para generar archivo con paths absolutos de OGLE
# -----------------------------------------------------------------------------

import os

def get_paths(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))


def writePathsFile(directory, result_file):
    
    files = get_paths(directory)
    
    with open(result_file, 'w') as archivo:
        for f in files:
            archivo.write(f + '\n')

if __name__ == '__main__':

    directory = "/Users/npcastro/Dropbox/OGLE/"
    result_file = '/Users/npcastro/workspace/Features/lightcurves_paths/OGLE.txt'

    writePathsFile(directory, result_file)
