import matplotlib.pyplot as plt
import numpy as np
import matplotlib.mlab as mlab

def graf_hist(values, real, naive, feature_name):
	"""

	Parameters
	----------
	values: Valores con los que generar el histograma (features sampleadas)
	real: Valor real de la feature
	naive: Valor calculado sin samplear
	feature_name: Nombre de la feature
	"""
	mean = np.mean(values)
	std = np.std(values)

	x = np.linspace(mean - 4*std,mean +4*std,100)

	plt.figure()
	plt.plot(x,mlab.normpdf(x,mean,std), 'k--')

	n, bins, patches = plt.hist(values, 25, normed=1, histtype='bar', color = 'c', alpha=0.6)

	plt.axvline(x= real, color = 'r', label=u'Real value')
	plt.axvline(x= naive, color = 'g', label=u'Naive value')
	#plt.ylim(0.0, 0.5)

	#plt.xlim(-0.1, 1.6)

	plt.title(feature_name, size=18)
	plt.xlabel('Feature Value', size=14)
	#plt.ylabel('Probability density', rotation = 'horizontal', labelpad=60, size=14)


	plt.legend(loc='upper right')

	plt.show()
	plt.close()

def sample_hist(values, real = None, feature_name='Feature', save_path='', show=False):
	"""

	Parameters
	----------
	values: Valores con los que generar el histograma (features sampleadas)
	real: Valor real de la feature
	feature_name: Nombre de la feature
	"""
	mean = np.mean(values)
	std = np.std(values)

	x = np.linspace(mean - 4*std,mean +4*std,100)

	plt.figure(figsize=(6*3.13,9))
	plt.plot(x,mlab.normpdf(x,mean,std), 'k--')

	n, bins, patches = plt.hist(values, 30, normed=1, histtype='bar', color = 'c', alpha=0.6)

	plt.axvline(x= real, color = 'r', label=u'Real value')

	plt.title(feature_name, size=18)
	plt.xlabel('Feature Value', size=14)
	#plt.ylabel('Probability density', rotation = 'horizontal', labelpad=60, size=14)


	plt.legend(loc='upper right')

	if show:
		plt.show()
		
	if save_path != '':
		plt.savefig(save_path + feature_name + '.png')

	plt.close()