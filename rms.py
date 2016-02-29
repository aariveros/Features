import pandas as pd
import numpy as np

import lightcurves.lc_utils as lu

def rms(true_value, sampled_values):
	"""Es el promedio de las diferencias de los valores sampleados con el valor
	real. Se le saca la raiz para compensar por la potencia al cuadrado y se
	divide por la desviacion standard para darle mayor significado.
	"""
	n = len(sampled_values)
	std = np.var(sampled_values)

	aux = map(lambda x: (x - true_value) ** 2, sampled_values)
	aux = sum(aux) / n

	if std == 0:
		return np.sqrt(aux)
	else:
		return np.sqrt(aux) / std

if __name__ == '__main__':

	feats = ['Amplitude','AndersonDarling','Autocor_length','Beyond1Std','Con','Eta_e','LinearTrend',
	'MaxSlope','Mean','Meanvariance','MedianAbsDev','MedianBRP','PairSlopeTrend','PercentAmplitude',
	'Q31','Rcs','Skew','SlottedA_length','SmallKurtosis','Std','StetsonK','StetsonK_AC']

	# feat_name = 'Beyond1Std'
	percentage = '10'

	for feat_name in ['Mean']:
		lc_ids = []
		rms_errors = []
		mean_values = []

		true_values = pd.read_csv('/Users/npcastro/workspace/Features/sets/MACHO_temp/Macho_regular_set_' + percentage + '.csv', index_col=0)
		true_values = true_values.reset_index().drop_duplicates(subset='index', take_last=True).set_index('index')
		true_values = true_values[feat_name]

		# sampled_feats_paths = lu.get_paths('/Users/npcastro/Lab/Samples_Features/MACHO/uniform/' + percentage + '%/', extension='.csv')
		sampled_feats_paths = lu.get_paths('/Users/npcastro/Lab/Malas/uniform/' + percentage + '%/', extension='.csv')
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
			rms_errors.append(rms(true_value, sampled_values))

		print np.mean(rms_errors)