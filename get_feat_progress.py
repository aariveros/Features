import pandas as pd
import lightcurves.lc_utils as lu
import lightcurves.features as ft


# path = "/Users/npcastro/workspace/Features/lightcurves_paths/Be_lc.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/CEPH.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/EB.txt"
path = "/Users/npcastro/workspace/Features/lightcurves_paths/longperiod_lc.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/microlensing_lc.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/non_variables.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/quasar_lc.txt"
# path = "/Users/npcastro/workspace/Features/lightcurves_paths/RRL.txt"

paths_azules, paths_rojas = lu.get_lightcurve_paths(path, separate_bands=True)

criterio = lu.var_completeness


# Para cada curva de luz
for path_azul, path_roja in zip(paths_azules, paths_rojas):

	# Obtengo el id de la curva
	macho_id = lu.get_lightcurve_id(path_azul)

	# try:
	# Abro ambas bandas, filtro datos extremos y combino en un frame
	azul = lu.open_lightcurve(path_azul)
	azul = lu.filter_data(azul)

	roja = lu.open_lightcurve(path_roja)
	roja = lu.filter_data(roja)

	curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')

	# Si no hay suficientes puntos para calcular las features con ambas bandas me salto la curva de luz
	if len(curva.index) < 100:
		print 'curva ' + macho_id + ' descartada por falta de puntos sincronizados'
		# continue	

	# Para cada feature calculo el valor y la confianza y los agrego a una lista
	header = '#Punto Sigma_B Eta_B stetson_L_B CuSum_B B-R stetson_J stetson_K skew kurt std beyond1_std max_slope amplitude med_abs_dev \n'
	
	feat_values = []

	# i determina la fraccion de puntos que se van a utilizar de la curva total (queremos samplear 100 veces el valor de a feature)
	i = len(curva.index) / 100

	try:
		print('###### Variability index ######')
		x_values, y_values = lu.feature_progress(curva, ft.var_index, i)
		puntos = x_values
		feat_values.append(y_values)

		print('########## Eta #############')
		x_values, y_values = lu.feature_progress(curva, ft.eta, i)
		feat_values.append(y_values)

		print('######### Stetson L ##########')
		x_values, y_values = lu.feature_progress(curva, ft.stetsonL, i)
		feat_values.append(y_values)

		print('######### CumSum ###########')
		x_values, y_values = lu.feature_progress(curva, ft.cu_sum, i)
		feat_values.append(y_values)

		print('########## B-R ############')
		x_values, y_values = lu.feature_progress(curva, ft.B_R, i)
		feat_values.append(y_values)

		print('########## Stetson J ############')
		x_values, y_values = lu.feature_progress(curva, ft.stetsonJ, i)
		feat_values.append(y_values)

		print('########## Stetson K ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.stetsonK, i)
		feat_values.append(y_values)

		print('########## Skewness ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.skew, i)
		feat_values.append(y_values)

		print('########## Kurtosis ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.small_kurtosis, i)
		feat_values.append(y_values)

		print('########## Kurtosis ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.small_kurtosis, i)
		feat_values.append(y_values)

		print('########## Standard Deviation ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.std, i)
		feat_values.append(y_values)

		print('########## Beyond 1 std ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.beyond1_std, i)
		feat_values.append(y_values)

		print('########## Max Slope ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.max_slope, i)
		feat_values.append(y_values)

		print('########## Amplitude ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.amplitude, i)
		feat_values.append(y_values)

		print('########## Median absolute deviation ############')
		x_values, y_values = lu.feature_progress(curva['azul'], ft.median_abs_dev, i)
		feat_values.append(y_values)

		io.save_lc(path_azul, header, puntos, feat_values)
		
	except(KeyboardInterrupt):
		break
	except:
		print '\n'
		print 'curva ' + macho_id + ' descartada por error'
		print '\n'