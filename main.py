# Grafica la evolucion de un set de features para una muestra de
# cada clase de curvas.

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

    features = [ft.var_index, ft.eta, ft.cu_sum, ft.B_R, ft.stetsonL, ft.median_abs_dev]
    feature_names = ['Variability Index', 'Eta', 'Cum Sum', 'B-R', 'StetsonL', 'Median absolute deviation' ]

    clases = { 'Be_lc': 0, 'CEPH': 255, 'EB': 457, 'longperiod_lc': 967, 'microlensing_lc': 1697, 'non_variables': 2862, 'quasar_lc': 12527, 'RRL':12645 }

    # Para cada clase de estrella
    for clase in clases.keys():

        print ('\n' + '###### ' + clase + ' ######' + '\n')

        # Para cada feature
        for j in xrange(len(features)):
            feature = features[j]
            feature_name = feature_names[j]

            print '\n' + feature_name + '\n'

            a = clases[clase]
            b = a + 1

            # Tomo 10 estrellas como muestra
            for i in xrange(10):
                azul = lu.open_lightcurve( paths[a] )
                azul = lu.filter_data(azul)
                roja = lu.open_lightcurve( paths[b])
                roja = lu.filter_data(roja)

                # Combinacion de bandas en un solo dataframe
                # Ojo que el join es inner, lo que solo es necesario para la StetsonL

                # if feature_name == 'StetsonL':
                #     curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')
                # else:
                #     curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='outer')

                curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')

                macho_id = lu.get_lightcurve_id(paths[a])
                print macho_id

                ###### Variability index ######
                x_values, y_values = st.feature_progress(curva, feature, 1)
                #io.graf_feature_progress(y_values, title)
                #io.graf_lc_and_feature_progress(curva.index.tolist(), curva['azul']['mag'].tolist(), y_values, macho_id, clase, feature_name)
                io.graf_lc_and_feature_progress_unnormalized(curva.index.tolist(), curva['azul']['mag'].tolist(), y_values, macho_id, clase, feature_name)

                a += 2
                b += 2

