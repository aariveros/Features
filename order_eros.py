# coding=utf-8  

# Separa las curvas de algun catalogo en distintas carpetas según clase

# -----------------------------------------------------------------------------

import shutil
import re

import pandas as pd

import lightcurves.lc_utils as lu


def get_id(path):
    """Recibe un path absoluto a un archivo de una curva de luz de EROS y 
    retorna el id de la curva
    """
    pattern = re.compile('lm.*[^.time]')
    return pattern.search(path).group()

def get_new_class(clase):
    
    if clase in ['EA', 'B_Lyrae', 'EA_up']:
        return 'EA'

    elif clase in ['HADS', 'LADS']:
        return 'dsct'

    elif clase in ['RRab', 'RRc', 'RRd', 'Blazhko']:
        return 'rrlyr'

    elif clase in ['t2cep', 'ACEP']:
        return 'cep'

    else:
        return clase
    

if __name__ == '__main__':

    catalog = 'CATALINA'
    lc_path_file = '/Users/npcastro/workspace/Features/lightcurves_paths/'
    lc_files = lu.get_lightcurve_paths(lc_path_file, catalog=catalog)

    result_dir = '/Users/npcastro/Lab/Catalina-II/'

    error_count = 0

    for path in lc_files:
       if '.csv' in path:
           try:
               lc_id = lu.get_lightcurve_id(path, catalog=catalog)
               clase = get_new_class(lu.get_lightcurve_class(path, catalog=catalog))
               shutil.copy(path, result_dir + clase )
           except KeyError:
               print lc_id
               error_count += 1