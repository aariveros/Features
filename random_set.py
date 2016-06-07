# coding=utf-8

# Toma un set de entrenamiento y genera uno con incertidumbre aleatoria en las 
# variables
# -----------------------------------------------------------------------------

import pandas as pd
import random
import numpy as np

def add_noise(data, level):
	"""Toma un dataframe normal (cada columna es una feature y la ultima es class), 
		y le agrega incertidumbre. Ademas agrega la columan weight que ocupan mis modelos

	data: dataframe
	level: porcentaje del rango. Se usa como el valor maximo de incertidumbre que se le da a un punto
	"""

	columns = data.columns[0:-1]
	
	# Obtengo los rangos para cada variable. Despues la incertidumbre se pone como fraccion de estos.
	rangos = {col: (data[col].max() - data[col].min()) for col in columns}

	df = {}

	for col in columns:	# no considero la clase
		feature = data[col]

		std = []

		for i in range(feature.size):
			noise = np.random.uniform(0, level) / 100.0
			std.append(rangos[col] *  noise)

		df[col] = std

	return pd.DataFrame(df, index=data.index)
	

if __name__ == '__main__':

	dataset_path = '/Users/npcastro/Desktop/Datasets/Robot/sensor_readings_24.csv'
	result_dir = '/Users/npcastro/Desktop/Datasets/Noise/'
	
	data = pd.read_csv(dataset_path)

	noise_levels = range(5, 70, 5)

	for u in noise_levels:
		np.random.seed(1)

		u_data = add_noise(data, u)
		u_data.to_csv(result_dir + 'Robot_' + str(u) +'.csv')