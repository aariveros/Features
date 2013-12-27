import pandas as pd
import lightcurves.lc_utils as lu
import lightcurves.features as ft
import lightcurves.lc_IO as io

# Paths a las curvas de cada clase
paths ='/Users/npcastro/workspace/Features/lightcurves_paths/Be_lc.txt '
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/RRL.txt	'		
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/microlensing_lc.txt'
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/CEPH.txt'		
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/non_variables.txt'
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/EB.txt'			
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/longperiod_lc.txt'
# path ='/Users/npcastro/workspace/Features/lightcurves_paths/quasar_lc.txt'
# path = '/Users/npcastro/workspace/Features/lightcurves_paths/Todas.txt'

paths_azules, paths_rojas = lu.get_lightcurve_paths(path, separate_bands=True)

criterio = lu.var_completeness

# Creo los archivos donde voy a escribir los resultados
header = 	'#Macho_id Sigma_B Sigma_B_conf Eta_B Eta_B_conf stetson_L_B stetson_L_B_conf CuSum_B CuSum_B_conf B-R B-R_conf' +
			'stetson_J stetson_J_conf stetson_K stetson_K_conf skew skew_conf kurt kurt_conf std std_conf beyond1_std beyond1_std_conf' +
			'max_slope max_slope_conf amplitude amplitude_conf med_abs_dev med_abs_dev_conf class\n'

io.init_results_file(header)

# Para cada curva de luz
for path_azul, path_roja in zip(paths_azules, paths_rojas):
	
	try:
		# Abro ambas bandas, filtro datos extremos y combino en un frame
		azul = lu.open_lightcurve(path_azul)
		azul = lu.filter_data(azul)

		roja = lu.open_lightcurve(path_roja)
		roja = lu.filter_data(roja)

		curva = pd.concat([azul, roja], axis=1, keys=['azul', 'roja'], join='inner')

		# Obtengo el id de la curva
		macho_id = lu.get_lightcurve_id(path_azul)

		# Si no hay suficientes puntos para calcular las features con ambas bandas me salto la curva de luz
		if len(curva.index) < 100:
			print 'curva ' + macho_id + ' descartada por falta de puntos sincronizados'
			continue		

		# Para cada feature calculo el valor y la confianza y los agrego a una lista
		features = []
		confianzas = []


		print('########## Eta #############')
		x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.eta, criterio)
		features.append(y_values)
		confianzas.append(completitud)


		print('###### Variability index ######')
		x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.var_index, criterio)
		features.append(y_values)
		confianzas.append(completitud)


		print('######### Stetson L ##########')
		x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.stetsonL, criterio, 10)
		features.append(y_values)
		confianzas.append(completitud)


		print('######### CumSum ###########')
		x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.cu_sum, criterio, 10)
		features.append(y_values)
		confianzas.append(completitud)


		print('########## B-R ############')
		x_values, y_values, completitud = lu.get_feat_and_comp(curva, ft.B_R, criterio)
		features.append(y_values)
		confianzas.append(completitud)


		porcentajes = [20,40,60,80,100]

		for p in porcentajes:
			
			# Agrego las features y sus confianzas al string de resultado
			linea = macho_id + " "
			for f in range(len(features)):
				total = len(confianzas[f])
				indice = (total * p/100) - 1

				linea = linea + str(features[f][indice]) + " " + str(confianzas[f][indice]) + " "

			linea = linea + str(lu.get_lc_class(path_azul))
			io.save_line(linea, p)

	except(KeyboardInterrupt):
		break
	except:
		print '\n'
		print 'curva ' + macho_id + ' descartada por error'
		print '\n'