import matplotlib.pyplot as plt
import pandas as pd
import lightcurves.lc_utils as lu
import lightcurves.features as ft

paths = lu.get_lightcurve_paths()

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL
a, b = 0, 1 

azul = lu.open_lightcurve( paths[a] )
azul = lu.filter_data(azul)

# Combinacion de bandas en un solo dataframe
roja = lu.open_lightcurve( paths[b])
roja = lu.filter_data(roja)
curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')


# Graficar curva

# plt.figure(1)
# plt.plot( curva['azul']['mag'], 'bo')
# plt.title('algo')
# plt.show()


###### Variability index ######
x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.var_index, lu.trust)
lu.graf_feature( x_values, y_values, 'Variability index', x_values[2:], completitud, 2)


########## Eta #############
x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.eta, lu.trust)
lu.graf_feature( x_values, y_values, 'Eta', x_values[2:], completitud, 3)


######### Con #############
x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.con, lu.trust)
lu.graf_feature( x_values, y_values, 'Con', x_values[2:], completitud, 4)


######### CumSum ###########
x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.cu_sum, lu.trust, 10)
lu.graf_feature( x_values, y_values, 'CuSum', x_values[2:], completitud, 5)


# ########## B-R ############
# plt.subplot(2, 1, 1)
# plt.plot( curva['azul']['mag'], 'bo')

# plt.subplot(2, 1, 2)
# plt.plot( curva['roja']['mag'], 'bo')
# plt.show()

x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.B_R, lu.trust)
lu.graf_feature( x_values, y_values, 'B-R', x_values[2:], completitud, 6)


# ######### Stetson L ##########
x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.stetsonL, lu.trust, 10)
lu.graf_feature( x_values, y_values, 'Stetson-L', x_values[2:], completitud, 7)