# coding=utf-8

# Script para generar archivo con paths absolutos de OGLE
# -----------------------------------------------------------------------------

import os
import lightcurves.lc_utils as lu


def writePathsFile(directory, result_file):
    
    # files = get_paths(directory)
    files = lu.get_paths(directory, '.dat')
    
    with open(result_file, 'w') as archivo:
        for f in files:
            archivo.write(f + '\n')

if __name__ == '__main__':

    # directory = "/n/seasfs03/IACS/TSC/ncastro/CATALINA/"
    # result_file = '/n/home09/ncastro/workspace/Features/lightcurves_paths/CATALINA.txt'

    directory = "/Users/npcastro/Desktop/VISTA/"
    result_file = '/Users/npcastro/workspace/Features/lightcurves_paths/VISTA.txt'

    writePathsFile(directory, result_file)
