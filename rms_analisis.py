# coding=utf-8

# Hago un analisis de la relacion entre el rms de las curvas fitteadas y
# y la calidad de las predicciones

# --------------------------------------------------------------------------

import pandas as pd

rms = pd.read_csv('/Users/npcastro/Dropbox/Resultados/RMSD/fitted/5.csv', index_col=0)
result = pd.read_csv('/Users/npcastro/Dropbox/Resultados/MACHO/Sampled/uniform/UF/Predicciones/result_5.csv', index_col=0)

df = rms.merge(result, how='inner', left_index=True, right_index=True)

# Elimino la clase repetida y las curvas con id repetido
b = df['class'] == df.original
c = b[b == False].index.tolist()
df = df.drop(c)
df = df.drop('class', axis=1)

group = df.groupby('original')

correct = df[df['original'] == df['predicted']]
correct_group = correct.groupby('original')

incorrect = df[df['original'] != df['predicted']]
incorrect_group = incorrect.groupby('original')