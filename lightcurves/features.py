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

def slotted_autocorrelation(lc, k=1, T=4):
    """
    lc: MACHO lightcurve in a pandas DataFrame
    k: lag (default: 1)
    T: tau (slot size in days. default: 4)
    """
    # make time start from 0
    lc.index = map(lambda x: x - min(lc.index), lc.index)

    # subtract mean from mag values
    lc['mag'] = lc['mag'].subtract(lc['mag'].mean())

    min_time = min(lc.index)
    max_time = max(lc.index)
    current_time = lc.index[0]
    lag_time = current_time + k*T

    N = 0
    product_sum = 0
    while lag_time < max_time - T/2.0:
        # get all the points in the two bins (current_time bin and lag_time bin)
        lc_points = lc[np.logical_and(lc.index >= current_time - T/2.0, lc.index <= current_time + T/2.0)]
        lc_points_lag = lc[np.logical_and(lc.index >= lag_time - T/2.0, lc.index <= lag_time + T/2.0)]

        current_time = current_time + T
        lag_time = lag_time + T

        if len(lc_points) == 0 or len(lc_points_lag) == 0:
            continue

        current_time_points = np.array(lc_points['mag'].tolist()).reshape((len(lc_points), 1))
        lag_time_points = np.array(lc_points_lag['mag'].tolist()).reshape((1, len(lc_points_lag)))
        mult_matrix = current_time_points.dot(lag_time_points)

        product_sum = product_sum + mult_matrix.sum()
        N = N + 1

    return product_sum/float(N - 1)

def get_avg_timestep(index):
    return (max(index) - min(index)) / len(index)


def period(mag, index):
    from scipy.signal import lombscargle

    x = np.array(index) - min(index)
    mag_mean, mag_std = np.mean(mag), np.std(mag)
    y = (np.array(mag) - mag_mean)/mag_std
    
    T_tot = np.amax(x) - np.amin(x)

    f_N = 0.5*(1/get_avg_timestep(index))    
    f = np.arange(4/T_tot, 10, 0.1/T_tot)
    f = f*2*np.pi

    P = lombscargle(np.ravel(x), np.ravel(y), np.ravel(f))

    f_max = f[P.argmax()]/(2*np.pi)
    return 1/f_max

  


  



