# coding=utf-8

# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import lightcurves.lc_utils as lu
import graf

catalog = 'MACHO'
percentage = '50'
feat = 'Eta_e'
lc_id = '101.20650.1216'

real_df = pd.read_csv('/Users/npcastro/workspace/Features/sets/MACHO_temp/Macho_regular_set_' + percentage + '.csv', index_col=0)

samples_paths = lu.get_paths('/Users/npcastro/Lab/Samples_Features/uniform/' + percentage + '%/', '.csv')
samples_paths = [x for x in samples_paths]

for s in samples_paths:
    if lc_id in s:
        lc_class = lu.get_lightcurve_class(s)
        path = s
        break

samples_df = pd.read_csv(path)


real_value = real_df.loc[lc_id][feat].tolist()
sampled_values = samples_df[feat].tolist()

fig = plt.figure()
ax = fig.add_subplot(111)

graf.graf_hist(sampled_values, 'Sampled values')
plt.axvline(x=real_value, color = 'r', label=u'Real value', linewidth=2.0)

plt.ylabel('Count')
plt.xlabel('Feature Value')

plt.title(feat + ' ' + lc_id)
plt.legend()

plt.show()
plt.close()
