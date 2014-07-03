# Toma un directorio de curvas y grafica la evolucion de un set de features para una muestra de
# cada clase de curvas

import pandas as pd
import lightcurves.lc_utils as lu
import lightcurves.features as ft
import lightcurves.lc_IO as io
import lightcurves.lc_stats as st

if __name__ == '__main__':
    
    # Ubicacion de las curvas
    # 0-253         Be_lc
    # 255-455       CEPH
    # 457-965       EB
    # 967-1695      longperiod_lc
    # 1697-2860     microlensing_lc
    # 2862-12525    non_variables
    # 12527-12643   quasar_lc
    # 12645-12646   RRL

    paths = lu.get_lightcurve_paths()

    a, b = 0, 1

    azul = lu.open_lightcurve( paths[a] )
    azul = lu.filter_data(azul)
    roja = lu.open_lightcurve( paths[b])
    roja = lu.filter_data(roja)

    # Combinacion de bandas en un solo dataframe
    # Ojo que el join es inner, lo que solo es necesario para la StetsonL
    curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')

    

