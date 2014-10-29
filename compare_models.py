# Este script toma una curva, le ajusta un gaussian process y genera graficos del ajuste (guardados en Graficos Ajuste GP)
# También compara los errores en los calculos de las features, para 

import lightcurves.lc_utils as lu
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Primero abro una curva de luz

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

paths = lu.get_lightcurve_paths()
a, b = 2864, 2865
azul = lu.open_lightcurve(paths[a])
roja = lu.open_lightcurve(paths[b])

# Curva completa
plt.errorbar(azul.index, azul['mag'], yerr=azul['err'], fmt=".b", ecolor='r', capsize=0)
plt.show()
plt.close()

# Curva sampleada al 10%
plt.errorbar(azul.index[0::10], azul['mag'].iloc[0::10], yerr=azul['err'][0::10], fmt=".b", ecolor='r', capsize=0)
plt.show()
