import pandas as pd
import numpy as np

import lightcurves.lc_utils as lu

def rms(true_values, sampled_values, lc_id, normalize=''):
	"""Es el promedio de las diferencias de los valores sampleados con el valor
	real. Se le saca la raiz para compensar por la potencia al cuadrado y se
	divide por la desviacion standard para darle mayor significado.
	"""
	n = len(sampled_values)
	true_value =  true_values.loc[lc_id]

	aux = map(lambda x: (x - true_value) ** 2, sampled_values)
	aux = np.sqrt(sum(aux) / n)
	
	if normalize == '':
		return aux
	elif normalize == 'Mean':
		return aux / np.mean(true_values)
	elif normalize == 'Range':
		rango = np.max(true_values) - np.min(true_values)
		return aux / rango
	elif normalize == 'Std':
		return aux / np.std(true_values)

if __name__ == '__main__':

	feats = ['Amplitude','AndersonDarling','Autocor_length','Beyond1Std','Con','Eta_e','LinearTrend',
	'MaxSlope','Mean','Meanvariance','MedianAbsDev','MedianBRP','PairSlopeTrend','PercentAmplitude',
	'Q31','Rcs','Skew','SlottedA_length','SmallKurtosis','Std','StetsonK','StetsonK_AC']

	# feat_name = 'Beyond1Std'
	percentage = '5'
	normalize = 'Std'

	print normalize + '\n'

	for feat_name in ['Mean']:
		lc_ids = []
		rms_errors = []
		mean_values = []

		true_values = pd.read_csv('/Users/npcastro/workspace/Features/sets/MACHO_temp/Macho_regular_set_' + percentage + '.csv', index_col=0)
		true_values = true_values.reset_index().drop_duplicates(subset='index', take_last=True).set_index('index')
		true_values = true_values[feat_name]

		sampled_feats_paths = lu.get_paths('/Users/npcastro/Lab/Samples_Features/uniform/' + percentage + '%/', extension='.csv')
		sampled_feats_paths = [x for x in sampled_feats_paths]

		for path in sampled_feats_paths:

			sampled_values = pd.read_csv(path)
			sampled_values = sampled_values[feat_name]
			lc_id = lu.get_lightcurve_id(path, catalog='MACHO')

			try:
				true_value = true_values.loc[lc_id]
				mean_values.append(np.mean(sampled_values))
			except KeyError:
				# print lc_id + ' no esta en los valores reales'
				continue

			lc_ids.append(lc_id)
			rms_errors.append(rms(true_values, sampled_values, lc_id, normalize=normalize))

		print feat_name + ': ' + str(np.mean(rms_errors))