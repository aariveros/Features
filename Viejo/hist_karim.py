# Hace histogramas con la importancia de las features a distintos niveles
# de completitud de las curvas

# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

N = 10

df = pd.read_csv('/Users/npcastro/Dropbox/Resultados/EROS/Tree/Regular/Metricas/feat_importance.csv', index_col=0)
aux = df.loc[100]
aux.sort(ascending=False)
top_feats = aux.iloc[0:N].index.tolist()

df = pd.read_csv('/Users/npcastro/Dropbox/Resultados/EROS/UTree/GP/Metricas/feat_importance.csv', index_col=0)
aux = df.loc[95]
aux.sort(ascending=False)
top_feats = aux.iloc[0:N].index.tolist()

colors = ['b', 'r', 'c', 'g', '#6666ff']

# No llego a 100 porque no estan los resultados para el 100% en UTree
fig, ax = plt.subplots()
ind = np.arange(N)  # Las posiciones de las barras
width = 0.1        # El ancho de las mismas

for i, p in enumerate([25,55,75,95]):
# for i, p in enumerate([25,50,75,100]):
    
    aux = df.loc[p]
    aux = aux[top_feats]

    bars = ax.bar(ind + width * i, aux.tolist(), width, color=colors[i], label=str((i+1)*25) + '%')

    # add some text for labels, title and axes ticks

ax.set_xticks(ind + width)
ax.set_xticklabels(aux.index.tolist())
ax.set_ylabel('Importance', rotation=0)
ax.set_xlabel('Feature')
ax.set_title('EROS UTree feature importance')
ax.set_ylim(0,0.16)
ax.legend()

plt.show()

