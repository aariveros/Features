import pandas as pd
import lightcurves.lc_utils as lu
import lightcurves.features as ft


path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/Be_lc.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/CEPH.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/EB.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/longperiod_lc.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/microlensing_lc.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/non_variables.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/quasar_lc.txt"
# path = "/Users/npcastro/Dropbox/Tesis/Codigo python/lightcurves_paths/RRL.txt"

paths_azules, paths_rojas = lu.get_lightcurve_paths(path, separate_bands=True)

criterio = lu.var_completeness


# Para cada curva de luz
for path_azul, path_roja in zip(paths_azules, paths_rojas):

	# Obtengo el id de la curva
	macho_id = lu.get_lightcurve_id(path_azul)

	try:
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
		header = '#Punto Sigma_B Eta_B stetson_L_B CuSum_B B-R\n'
		feat_values = []


		print('###### Variability index ######')
		x_values, y_values = lu.feature_progress(curva, ft.var_index, 10)
		puntos = x_values
		feat_values.append(y_values)


		print('########## Eta #############')
		x_values, y_values = lu.feature_progress(curva, ft.eta, 10)
		feat_values.append(y_values)


		print('######### Stetson L ##########')
		x_values, y_values = lu.feature_progress(curva, ft.stetsonL, 10)
		feat_values.append(y_values)


		print('######### CumSum ###########')
		x_values, y_values = lu.feature_progress(curva, ft.cu_sum, 10)
		feat_values.append(y_values)


		print('########## B-R ############')
		x_values, y_values = lu.feature_progress(curva, ft.B_R, 10)
		feat_values.append(y_values)

		lu.save_lc(path_azul, header, puntos, feat_values)
		
	except(KeyboardInterrupt):
		break
	except:
		print '\n'
		print 'curva ' + macho_id + ' descartada por error'
		print '\n'