import numpy as np
import pandas as pd
from scipy import stats

"""
Los siguientes metodos reciben todos un dataframe de una curva de luz
y retornan el valor de una feature particular.

Ahora, todas las features reciben ambas bandas, y un parametro que dice que banda utilizar, en caso
de que utilicen una sola. Por default se asume que se usa la banda azul
"""

# Usa una banda
def var_index(X):
	"""
	X: arreglo de valores	
	"""
	return np.std(X) / np.mean(X)

# Usa una banda
def eta(X):

	n = len(X)

	R = 1.0/((n - 1) * np.var(X))
	nSum = 0
    
 	for i in xrange(n - 1):
 		aux = X[i+1] - X[i] 
 		nSum += aux**2
	
	return R * nSum	

# Usa una banda
def con(X):
	
	n = len(X)
	
	if( n < 4 ):
		return 0

	mean = np.mean(X)
	std = np.std(X)

	minLimit = mean - 2*std
	maxLimit = mean + 2*std

	count = 0;

	for i in range( n - 2 ):
		if( (X[i] > maxLimit) or (X[i] < minLimit) ):
			if( (X[i + 1] > maxLimit) or (X[i + 1] < minLimit) ):
				if( (X[i + 2] > maxLimit) or (X[i + 2] < minLimit) ):
					count += 1

	return float(count) / (n - 2)


# Usa una banda
def cu_sum(X):
	
	n = len(X)
	media = np.mean(X)
	std = np.std(X)
	
	partial_sums = []

	aux = X[0] - media
	minimo = aux
	maximo = minimo
	partial_sums.append(aux)

	m = 1/( n * std )

	for i in xrange(0,n-1):
		aux = partial_sums[i] + (X[i] - media)
		partial_sums.append(aux)

		aux = m * aux
		if(aux > maximo):
			maximo = aux
		if(aux < minimo):
			minimo = aux

	return maximo - minimo

# Recibe ambas bandas de la curva
def B_R( X_azul, X_roja ):
	return np.mean(X_azul) - np.mean(X_roja)


# Ambas bandas
def stetsonL( X_azul, err_azul, X_roja, err_roja ):
	media_a, media_r = np.mean(X_azul), np.mean(X_roja)
	
	return stetsonJ(X_azul, err_azul, X_roja, err_roja, media_a, media_r) * stetsonK(X_azul, err_azul, media_a) / 0.798	


# Ambas bandas
def stetsonJ( X_azul, err_azul, X_roja, err_roja, media_a = None, media_r = None ):

	# Agrego esta linea para cuando se usa esta funcion sola como feature
	if media_a == None or media_r == None:
		media_a, media_r = np.mean(X_azul), np.mean(X_roja)

	n = len(X_azul)
	suma = 0
	for i in range(n):
		p_i = delta(X_azul, err_azul, i, media_a) * delta(X_roja, err_roja, i, media_r)
		suma += (np.sign(p_i) * np.sqrt(abs(p_i)))
	
	return (1.0/n)*suma

# Una sola banda
def stetsonK( X, err, media=None):

	if media == None:
		media = np.mean(X)

	n = len(X)

	num = 0
	den = 0

	for i in range(n):
		aux = delta(X, err, i, media)
		num += abs(aux)
		den += aux**2

	return (1/np.sqrt(n)) * num / np.sqrt(den)


# Recibe una sola banda
def delta( mag, err, pos, media ):
	n = len(mag)
	aux = np.sqrt((n / (n - 1)))
	return aux * ( (mag[pos] - media) / err[pos])

# Una sola banda
def skew (X):
	return stats.skew(X)

# Una sola banda
def small_kurtosis(mag):
	n = float(len(mag))
	media = np.mean(mag)
	std = np.std(mag)

	suma = 0
	for i in range(int(n)):
		suma += ((mag[i] - media) / std)**4

	c1 = n*(n + 1) / ((n - 1)*(n - 2)*(n - 3))

	c2 = 3 * (n - 1)**2 / ((n-2)*(n-3))

	return c1 * suma - c2

def std(X):
	return np.std(X)

def beyond1_std(mag, err):
	n = len(mag)
	media = np.average(mag, weights= 1 / np.array(err)**2)

	var = 0
	for i in xrange(n):
		var += ((mag[i]) - media)**2

	std = np.sqrt( (1.0/(n-1)) * var )

	frac = 0

	for i in xrange(n):
		punto = mag[i]

		if punto > media + std or punto < media - std:
			frac += 1

	return float(frac) / n

# Recibe un array de magnitudes y uno con el tiempo de las mediciones
def max_slope(mag, t_obs):	
	max_slope = 0

	index = t_obs

	for i in xrange(len(mag) - 1):
		slope = float(mag[i+1] - mag[i]) / (index[i+1] - index[i])

		if slope > max_slope:
			max_slope = slope

	return max_slope

def amplitude(mag):
	return (max(mag) - min(mag)) / 2

def median_abs_dev(mag):
	median = np.median(mag)

	devs = []

	for i in xrange(len(mag)):
		devs.append(abs(mag[i] - median))

	return np.median(devs)

  


  



