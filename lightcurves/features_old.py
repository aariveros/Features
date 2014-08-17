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
def var_index(curva, banda='azul'):
	mag = curva[banda]['mag'].tolist()
	return np.std(mag) / np.mean(mag)

# Usa una banda
def eta(curva, banda='azul'):
	curva = curva[banda]
	mag = curva['mag'].tolist()

	n = len(curva)

	R = 1.0/((n - 1) * np.var(mag))

	nSum = 0
    
 	for i in xrange(n - 1):
 		aux = mag[i+1] - mag[i] 
 		nSum += aux**2
	
	return R * nSum	

# Usa una banda
def con( curva, banda='azul' ):
	curva = curva[banda]
	n = len(curva.index)
	
	if( n < 4 ):
		return 0

	mag = curva['mag']

	mean = mag.mean()
	std = mag.std()

	minLimit = mean - 2*std
	maxLimit = mean + 2*std

	count = 0;

	for i in range( n - 2 ):
		if( (mag.iloc[i] > maxLimit) or (mag.iloc[i] < minLimit) ):
			if( (mag.iloc[i + 1] > maxLimit) or (mag.iloc[i + 1] < minLimit) ):
				if( (mag.iloc[i + 2] > maxLimit) or (mag.iloc[i + 2] < minLimit) ):
					count += 1

	return float(count) / (n - 2)


# Usa una banda
def cu_sum(curva, banda='azul'):
	mag = curva[banda]['mag'].tolist()
	n = len(mag)
	media = np.mean(mag)
	std = np.std(mag)
	
	partial_sums = []

	aux = mag[0] - media
	minimo = aux
	maximo = minimo
	partial_sums.append(aux)

	m = 1/( n * std )

	for i in xrange(0,n-1):
		aux = partial_sums[i] + (mag[i] - media)
		partial_sums.append(aux)

		aux = m * aux
		if(aux > maximo):
			maximo = aux
		if(aux < minimo):
			minimo = aux

	return maximo - minimo

# Recibe ambas bandas de la curva
def B_R( curva ):
	return curva['azul']['mag'].mean() - curva['roja']['mag'].mean()

# Ambas bandas
def stetsonL( curva ):
	media_a, media_r = curva['azul']['mag'].mean(), curva['roja']['mag'].mean() 
	return stetsonJ(curva, media_a, media_r) * stetsonK(curva, media_a, 'azul') / 0.798	


# Ambas bandas
def stetsonJ( curva, media_a = None, media_r = None ):
	azul_mag = curva['azul']['mag'].tolist()
	azul_err = curva['azul']['err'].tolist()

	roja_mag = curva['roja']['mag'].tolist()
	roja_err = curva['roja']['err'].tolist()

	# Agrego esta linea para cuando se usa esta funcion sola como feature
	if media_a == None or media_r == None:
		media_a, media_r = np.mean(azul_mag), np.mean(roja_mag)

	n = len(azul_mag)
	suma = 0
	for i in range(n):
		p_i = delta(azul_mag, azul_err, i, media_a) * delta(roja_mag, roja_err, i, media_r)
		suma += (np.sign(p_i) * np.sqrt(abs(p_i)))
	
	return (1.0/n)*suma

# Una sola banda
def stetsonK( curva, media=None, banda='azul'):
	
	mag = curva[banda]['mag'].tolist()
	err = curva[banda]['err'].tolist()

	if media == None:
		media = np.mean(mag)

	n = len(mag)

	num = 0
	den = 0

	for i in range(n):
		aux = delta(mag, err, i, media)
		num += abs(aux)
		den += aux**2

	return (1/np.sqrt(n)) * num / np.sqrt(den)



# Recibe una sola banda
def delta( mag, err, pos, media ):
	n = len(mag)
	aux = np.sqrt((n / (n - 1)))
	return aux * ( (mag[pos] - media) / err[pos])

# Una sola banda
def skew (curva, banda='azul'):
	curva = curva[banda]
	return stats.skew(curva['mag'])

# Una sola banda
def small_kurtosis(curva, banda='azul'):
	mag = curva[banda]['mag']
	n = float(len(mag))
	media = np.mean(mag)
	std = np.std(mag)

	suma = 0
	for i in range(n):
		suma += ((mag[i] - media) / std)**4

	c1 = n*(n + 1) / ((n - 1)*(n - 2)*(n - 3))

	c2 = 3 * (n - 1)**2 / ((n-2)*(n-3))

	return c1 * suma - c2

def std(curva, banda='azul'):
	curva = curva[banda]
	return curva['mag'].std()

def beyond1_std(curva, banda='azul'):
	mag = curva[banda]['mag']
	n = len(mag)
	
	media = np.average(mag, weights= 1 / curva[banda]['err']**2)

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

def max_slope(curva, banda='azul'):	
	mag = curva[banda]['mag']
	max_slope = 0

	index = curva.index.tolist()

	for i in xrange(len(mag) - 1):
		slope = float(mag[i+1] - mag[i]) / (index[i+1] - index[i])

		if slope > max_slope:
			max_slope = slope

	return max_slope


def amplitude(curva, banda='azul'):
	curva = curva[banda]
	return (curva['mag'].max() - curva['mag'].min()) / 2

def median_abs_dev(curva, banda='azul'):
	mag = curva[banda]['mag'].tolist()
	median = np.median(mag)

	devs = []

	for i in xrange(len(mag)):
		devs.append(abs(mag[i] - median))

	return np.median(devs)


def period( curva, banda='azul' ):
	curva = curva[banda]

	t = np.array(curva['mjd'])[np.newaxis]
	h = np.array(curva['mag'])   

	mean = np.mean(h)
	variance = np.std(h)

	N = len(h);
	T = np.amax(t) - np.amin(t)

	hifac = 10

	f = np.transpose(np.arange(4/T,hifac*N/(2*T),1/T))

	w = np.array(2*np.pi*f);

	tau = np.divide(np.arctan2(sum(np.sin(2*w*t.T),0), sum(np.cos(2*w*t.T),0)), 2*w)

	cterm = np.cos(w*t.T - np.tile(w*tau,(1,len(t)))).T
	sterm = np.sin(w*t.T - np.tile(w*tau,(1,len(t)))).T

	P = (np.divide(np.square(sum(np.inner(cterm,np.diag(h-mean)),1)), sum(np.square(cterm),1)) + np.divide(np.square(sum(np.inner(sterm,np.diag(h-mean)),1)), sum(np.square(sterm),1)))/(2*variance)
	
	return 1/f[P.argmax()]


# Estas features estan mal hechas. Tienen que entrenarse con un set de curvas de luz
# clasificadas para poder usarse


def nAbove4( curva ):
	x_values, y_values = complete_ac( curva )

	desviacion = np.std(y_values)
	pass

def nBelow4( curva ):
	pass

# Recibe una sola banda
def stetsonK_ac( curva ):

	x_values, y_values = complete_ac( curva )
	desviaciones = []
	for i in range( len(y_values)):
		desviaciones.append( np.std(y_values[0:i+1]))

	d = {'mag':  pd.Series(y_values), 'err': pd.Series(desviaciones)}
	df = pd.DataFrame(d)
	df['err'].iloc[0] = curva['err'].mean()
	# df['err'].iloc[1] = curva['err'].mean()

	# return stetsonK( y_values, np.mean(y_values))
	return stetsonK( df, df['mag'].mean())

"""
 Calcula la funcion de autocorrelacion, para una serie de puntos (curva),
 con parametro time_lag.
"""

def auto_correlation( curva, time_lag, media, var ):
	n = len( curva.index )
	# media = curva['mag'].mean()
	# var = curva['mag'].var()
	c = 1.0/((n - time_lag)*var)

	suma = 0
	for i in range( n - time_lag ):
		suma += (curva['mag'].iloc[i] - media) * (curva['mag'].iloc[i + time_lag] - media)

	return c * suma

"""
 Calcula la funcion de autocorrelacion, para todos los posibles time_lags retornando
 en una lista los valores AC y los time lags. 
"""

def complete_ac( curva ):
	y_values = []
	x_values = []
	n = len(curva.index)
	media = curva['mag'].mean()
	var = curva['mag'].var()

	for i in range(n - 1):
		x_values.append(i)
		y_values.append(auto_correlation(curva, i, media, var))

	return x_values, y_values
  


  


