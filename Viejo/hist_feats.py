# coding=utf-8

# Hace histogramas de la distribución del valor de las features mas importantes
# para algunas curvas de EROS

# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import lightcurves.lc_utils as lu
import os

def get_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if '.csv' in f:
                yield(os.path.abspath(os.path.join(dirpath, f)))

N = 10

# Obtengo las N features mas importantes
feat_df = pd.read_csv('/Users/npcastro/Dropbox/Resultados/MACHO/Tree/Regular/Metricas/feat_importance.csv', index_col=0)
aux = feat_df.loc[100]
aux.sort(ascending=False)
top_feats = aux.iloc[0:N].index.tolist()

paths = get_paths('/Users/npcastro/Desktop/temp/25%/')

for path in paths:
    macho_id = lu.get_lightcurve_id(path)
    macho_class = lu.get_lc_class_name(path)
    archivo = macho_id + '.csv'

    for feat in top_feats:

        rows = 2
        cols = 2

        f, axarr = plt.subplots(rows, cols, sharex=True, sharey=True, figsize=(16,9))

        percentages = ['25', '50', '75', '100']

        ymin, ymax, xmin, xmax = 0,0,0,0

        for i in xrange(rows):
            for j in xrange(rows):
                aux_path = '/Users/npcastro/Desktop/temp/' + percentages[i * cols + j] + '%/' + macho_class +'/' + archivo
                df = pd.read_csv(aux_path)
                x = df[feat]

                if len(x.unique()) != 1:
                    x = x[np.abs(x - x.mean()) < 3 * x.std()]

                ax = axarr[i, j]

                n, bins, patches = ax.hist(x.tolist(), 50, facecolor='green', alpha=0.75, label= 'std=' + "%0.4f" % x.std())

                ax.axvline(x.mean(), color='b', linestyle='dashed')

                ax.set_ylabel('Freq', rotation=0)
                ax.set_xlabel('Feature value')
                ax.legend()

        plt.suptitle( macho_class + ' ' + feat + ' value distribution', fontsize=20)
        # plt.show()

        plt.savefig('/Users/npcastro/Desktop/hists feat_importance/' + macho_class + '/' + macho_id + '_' + feat + '.png',
                    dpi=f.dpi)
        plt.close()

    #     break
    # break

