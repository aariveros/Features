# coding=utf-8

# toma un set de entrenamiento y genera n datasets sampleando con cierta
# incertidumbre de el
# -----------------------------------------------------------------------------

import pandas as pd
import numpy as np

def sample_set(data, noise):

	# Guardo la clase para despues
	y = data['class']
	data = data.drop('class', axis=1)

	df = {}

	for name, col in data.iteritems():
		noise_col = noise[name]
		aux = []

		for i in xrange(col.size):
			value = col.iloc[i]
			std = noise_col.iloc[i]

			sampled_value = np.random.normal(value, std)
			aux.append(sampled_value)

		df[name] = aux

	df = pd.DataFrame(df, index = data.index)
	df['class'] = y
	return df

if __name__ == '__main__':

	name = 'Robot'

	data_dir = '/Users/npcastro/Desktop/Datasets/Data/'
	noise_dir = '/Users/npcastro/Desktop/Datasets/Noise/'
	result_path = '/Users/npcastro/Desktop/Datasets/Sampled/'

	np.random.seed(1)

	aux = range(5,70,5)
	for u in aux:
	
		noise_path = noise_dir + name + '_' + str(u) +'.csv'
		noise = pd.read_csv(noise_path, index_col=0)

		path = data_dir = '/Users/npcastro/Desktop/Datasets/Data/' + name + '.csv'
		data = pd.read_csv(path)

		n = 100
		for i in xrange(n):

			sampled_frame = sample_set(data, noise)
			sampled_frame.to_csv(result_path + str(u) + '%/' + name + '_' + str(i) +'.csv') 