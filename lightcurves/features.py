import numpy as np
import pandas as pd
from scipy import stats

"""
	Los siguientes metodos reciben todos un dataframe de una curva de luz
	y retornan el valor de una feature particular.
"""

# Usa una banda
def var_index( curva ):
	curva = curva['azul']
	return curva['mag'].std() / curva['mag'].mean()

# Usa una banda
def eta( curva ):
	curva = curva['azul']
	n = len(curva.index)

	R = 1.0/((n - 1) * curva['mag'].var())

	nSum = 0
    
 	for i in range(n - 1):
 		aux = curva['mag'].iloc[i+1] - curva['mag'].iloc[i] 
 		nSum += aux**2
	
	return R * nSum

# Usa una banda
def con( curva ):
	curva = curva['azul']
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
def cu_sum(curva):
	curva = curva['azul']
	n = len(curva.index)
	mag = curva['mag']
	media = mag.mean()
	std = mag.std()
	
	partial_sums = []

	aux = mag.iloc[0] - media
	minimo = aux
	maximo = minimo
	partial_sums.append(aux)

	m = 1/( n * std )

	for i in range(0,n-1):
		aux = partial_sums[i] + (mag.iloc[i] - media)
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

	# return stetsonJ(curva) * stetsonK(curva['azul']) / 0.798
	media_a, media_r = curva['azul']['mag'].mean(), curva['roja']['mag'].mean() 
	return stetsonJ(curva, media_a, media_r) * stetsonK(curva['azul'], media_a) / 0.798


# Ambas bandas
def stetsonJ( curva, media_a = None, media_r = None ):

	# Agrego esta linea para cuando se usa esta función sola como feature
	if media_a == None or media_r == None:
		media_a, media_r = curva['azul']['mag'].mean(), curva['roja']['mag'].mean()

	n = len(curva.index)
	suma = 0
	for i in range(n):
		p_i = delta(curva['azul'], i, media_a) * delta(curva['roja'], i, media_r)
		suma += (np.sign(p_i) * np.sqrt(abs(p_i)))
	
	return (1.0/n)*suma


# Una sola banda
def stetsonK( curva, media = None ):

	if media == None:
		media = curva['mag'].mean()

	n = len(curva.index)

	num = 0
	den = 0
	for i in range(n):
		aux = delta(curva,i, media)
		num += abs(aux)
		den += aux**2

	return (1/np.sqrt(n)) * num / np.sqrt(den)

# Recibe una sola banda
def delta( curva, pos, media ):

	n = len( curva.index )
	aux = np.sqrt((n / (n - 1)))
	# return aux * ((curva['mag'].iloc[pos] - curva['mag'].mean()) / curva['err'].iloc[pos])
	return aux * ((curva['mag'].iloc[pos] - media) / curva['err'].iloc[pos])

# Una sola banda
def skew (curva):
	return stats.skew(curva['mag'])

# Una sola banda
def small_kurtosis(curva):
	n = len(curva.index)
	media = curva['mag'].mean()

	suma = 0
	for i in range(n):
		suma += ((curva['mag'].iloc[i] - media) / curva['mag'].var())**4

	c1 = (n*(n + 1) / (n - 1)*(n - 2)*(n - 3))

	c2 = 3 * (n - 1)**2 / (n-2)*(n-3)

	return c1 * suma - c2


def std(curva):
	return curva['mag'].std()

def beyond1_std(curva):
	n = len(curva.index)
	
	media = np.average(curva['mag'], weights=curva['err'])

	var = 0
	for i in range(n):
		var += ((curva['mag'].iloc[i]) - media)**2

	std = np.sqrt( (1.0/(n-1)) * var )

	frac = 0

	for i in range(n):
		punto = curva['mag'].iloc[i]

		if punto > media + std or punto < media - std:
			frac += 1

	return float(frac) / n

def max_slope(curva):
	max_slope = 0

	for i in range(len(curva.index) - 1):
		slope = float(curva['mag'].iloc[i+1] - curva['mag'].iloc[i]) / (curva.index.values[i+1] - curva.index.values[i])

		if slope > max_slope:
			max_slope = slope

	return max_slope


def amplitude(curva):
	return curva['mag'].max() - curva['mag'].min()

def median_abs_dev(curva):
	median = np.median(curva['mag'])

	devs = []

	for i in range(len(curva.index)):
		devs.append(abs(curva['mag'].iloc[i] - median))

	return np.median(devs)


def period( curva ):
	curva = curva['azul']

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
  


  



