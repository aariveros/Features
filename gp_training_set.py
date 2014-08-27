# Este script ajusta un gp sobre cada curva de la base de datos. 
# Luego samplea un grupo de curvas de ese gp calcula un set de features para esas curvas
# Y a partir de los valores resultantes genera una distribucion gaussiana.

# --------------------------------------------------------------------------
from sklearn.gaussian_process import GaussianProcess
import lightcurves.lc_utils as lu
import pandas as pd
import numpy as np

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

def main():
	feature_values = {
		'var_index': [],
		'eta': [],
		'CuSum': [],
		'B-R': [],
		'StetsonL': [],
		'StetsonJ': [],
		'StetsonK': [],
		'Skew': [],
		'small_kurtosis': [],
		'std': [],
		'beyond1_std': [],
		'max_slope': [],
		'amplitude': [],
		'median_abs_dev': [],
	}


	header = ''
	for f in feature_values.keys():
		header = header + f + '.l,' + f + '.mean,' + f + '.r,' + f + '.std,' 

	header = header + 'weight,class\n'

	archivo = open('gp_set.txt', 'w')
	archivo.write(header)
	archivo.close()



	# --------------------------------------------------------------------------
	# Abro la curva y la corto a un porcentaje dado
	paths_azules, paths_rojas = lu.get_lightcurve_paths( separate_bands=True)

	paths_azules = paths_azules[300:]

	for path_azul in paths_azules:

		# para asegurarme de que sean las misma curva
		path_roja = path_azul.replace('.B.', '.R.')

		azul = lu.open_lightcurve(path_azul)
		try:
			roja = lu.open_lightcurve(path_roja)
		except:
			continue

		curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')
		clase = lu.get_lc_class_name(path_azul)

		if len(curva.index) < 210:
			continue	

		# --------------------------------------------------------------------------
		# percentage = 0.5

		mediana = np.median(curva.index)
		curva = curva.loc[curva.index[0]:mediana]

		a = min(curva.index)
		b = max(curva.index)

		percentage = (mediana - a) / (b - a)
		extra_time = 1.0 - percentage

		if len(curva.index) < 101:
			continue	


		# --------------------------------------------------------------------------
		# Preparo la curva de luz para el ajuste del GP
		n_sampled_points = 100

		t_obs_b, y_obs_b, err_obs_b, min_time_b, max_time_b = lu.prepare_lightcurve(curva['azul'], n_sampled_points)
		t_obs_r, y_obs_r, err_obs_r, min_time_r, max_time_r = lu.prepare_lightcurve(curva['roja'], n_sampled_points)


		# --------------------------------------------------------------------------
		# Ajusto dos GP tomando como error el que viene con las mediciones de las curvas
		dy = np.array(err_obs_b.T)[0]
		X_b = t_obs_b
		y_b = np.array(y_obs_b.T)[0]

		# Mesh the input space for evaluations of the real function, the prediction and its MSE
		# Instanciate a Gaussian Process model
		gp_b = GaussianProcess(corr='squared_exponential', theta0=1e-1,
		                     thetaL=1e-3, thetaU=1,
		                     nugget=(dy/(y_b + 0.0001))**2,
		                     random_start=100)

		dy = np.array(err_obs_r.T)[0]
		X_r = t_obs_r
		y_r = np.array(y_obs_r.T)[0]

		gp_r = GaussianProcess(corr='squared_exponential', theta0=1e-1,
		                     thetaL=1e-3, thetaU=1,
		                     nugget=(dy/(y_r + 0.0001))**2,
		                     random_start=100)

		# Fit to data using Maximum Likelihood Estimation of the parameters
		gp_b = gp_b.fit(X_b, y_b)
		gp_r = gp_r.fit(X_r, y_r)


		# --------------------------------------------------------------------------
		# Tomo curvas muestreadas del GP ajustado anteriormente

		number_of_sampled_curves = 100
		num_locs = n_sampled_points

		np.random.seed(1)

		feature_values = {
			'var_index': [],
			'eta': [],
			'CuSum': [],
			'B-R': [],
			'StetsonL': [],
			'StetsonJ': [],
			'StetsonK': [],
			'Skew': [],
			'small_kurtosis': [],
			'std': [],
			'beyond1_std': [],
			'max_slope': [],
			'amplitude': [],
			'median_abs_dev': [],
		}

		for i in xrange(number_of_sampled_curves):

			x_pred = np.asmatrix(np.linspace(min_time_b,max_time_b + extra_time,num_locs)).T
			y_pred, MSE = gp_b.predict(x_pred, eval_MSE=True)
			
			sigma_b = np.sqrt(MSE)
			aux_b = np.random.normal(y_pred, sigma_b)

			x_pred = np.asmatrix(np.linspace(min_time_r,max_time_r + extra_time,num_locs)).T
			y_pred, MSE = gp_r.predict(x_pred, eval_MSE=True)

			sigma_r = np.sqrt(MSE)
			aux_r = np.random.normal(y_pred, sigma_r)

			# Para cada feature calculo su valor y lo agrego a una lista
			import lightcurves.features as ft
			feature_values['var_index'].append(ft.var_index(aux_b))
			feature_values['eta'].append(ft.eta(aux_b))
			feature_values['CuSum'].append(ft.cu_sum(aux_b))
			feature_values['B-R'].append(ft.B_R(aux_b, aux_r))
			feature_values['StetsonL'].append(ft.stetsonL(aux_b, sigma_b, aux_r, sigma_r))
			feature_values['StetsonJ'].append(ft.stetsonJ(aux_b, sigma_b, aux_r, sigma_r))
			feature_values['StetsonK'].append(ft.stetsonK(aux_b, sigma_b))
			feature_values['Skew'].append(ft.skew(aux_b))
			feature_values['small_kurtosis'].append(ft.small_kurtosis(aux_b))
			feature_values['std'].append(ft.std(aux_b))
			feature_values['beyond1_std'].append(ft.beyond1_std(aux_b, sigma_b))
			feature_values['max_slope'].append(ft.max_slope(aux_b, x_pred))
			feature_values['amplitude'].append(ft.amplitude(aux_b))
			feature_values['median_abs_dev'].append(ft.median_abs_dev(aux_b))


		# --------------------------------------------------------------------------
		# Calculo la media, std, l y r. Despues escribo una linea en el archivo del set de entrenamiento 
		linea = ''

		for f in feature_values.keys():
			media = np.mean(feature_values[f])
			std = np.std(feature_values[f])
			l = media - 3 * std
			r = media + 3 * std

			linea = linea + str(l) + ',' + str(media) + ',' + str(r) + ',' + str(std) + ','

		linea = linea + '1.0' + ',' + clase + '\n'

		# Escribir linea
		archivo = open('gp_set.txt', 'a')
		archivo.write(linea)
		archivo.close()

if __name__ == '__main__':
	main()
