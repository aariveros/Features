# coding=utf-8

import pandas as pd
import numpy as np

import lightcurves.lc_utils as lu

def rms(true_values, sampled_values, lc_id, normalize=''):
	"""Es el promedio de las diferencias de los valores sampleados con el valor
	real. Se le saca la raiz para compensar por la potencia al cuadrado. 
	Existen diversas formas de normlización para poder comparar
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

	normalize = 'Std'
	catalog = 'MACHO'

	for percentage in xrange(5, 55, 5):
		print str(percentage) + '%'
		true_values = pd.read_csv('/Users/npcastro/workspace/Features/sets/MACHO_temp/Macho_regular_set_' + str(percentage) + '.csv', index_col=0)
		true_values = true_values.reset_index().drop_duplicates(subset='index', take_last=True).set_index('index')

		rms_dict = {}

		for feat_name in feats:
			lc_ids = []
			rms_errors = []
			lc_classes = []
		
			true_values_aux = true_values[feat_name]

			sampled_feats_paths = lu.get_paths('/Users/npcastro/Lab/Samples_Features/uniform/' + str(percentage) + '%/', extension='.csv')
			sampled_feats_paths = [x for x in sampled_feats_paths]

			for path in sampled_feats_paths:

				sampled_values = pd.read_csv(path)
				sampled_values = sampled_values[feat_name]
				lc_id = lu.get_lightcurve_id(path, catalog=catalog)
				lc_class = lu.get_lightcurve_class(path, catalog=catalog)

				try:
					true_value = true_values_aux.loc[lc_id]
				except KeyError:
					# print lc_id + ' no esta en los valores reales'
					continue

				lc_ids.append(lc_id)
				lc_classes.append(lc_class)
				rms_errors.append(rms(true_values_aux, sampled_values, lc_id, normalize=normalize))

			rms_dict[feat_name] = rms_errors

		rms_dict['class'] = lc_classes
		df = pd.DataFrame(rms_dict, index=lc_ids)
		df.to_csv('/Users/npcastro/Dropbox/Resultados/RMSD/' + str(percentage) + '%.csv')