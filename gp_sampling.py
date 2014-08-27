import lightcurves.lc_utils as lu
import lightcurves.features as ft
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random

def sample_LC(X, y, k, sigmas, x):
    """
    X: inputs vector with the location of the observed data
    y: vector with the observed values of f(x)
    k: covariance function
    sigmas: vector with the std of the observations
    x: vector with the desired prediction locations
    """
    
    num_obs = len(X)
    num_pred = len(x)
    
    # Mean of the predictions
    
    # K = K(X,X)
    # K_pred = K(X*,X)
    # K_ = K(X*,X*)
    
    K = np.matrix(np.zeros((num_obs, num_obs)))
    for i in xrange(num_obs):
        for j in xrange(num_obs):
            K[i,j] = k(X[i],X[j])
    
    K_pred = np.matrix(np.zeros((num_pred, num_obs)))
    for i in xrange(num_pred):
        for j in xrange(num_obs):
            K_pred[i,j] = k(x[i],X[j])
            
    K_ = np.matrix(np.zeros((num_pred, num_pred)))
    for i in xrange(num_pred):
        for j in xrange(num_pred):
            K_[i,j] = k(x[i],x[j])
    
    error = np.matrix(np.eye(num_obs)*sigmas)
    y = y.reshape(len(y),1)
    
    # Mean vector
    lc = np.ravel(K_pred * np.linalg.inv(K + error) * y)
    
    # Covariance Matrix
    cov = K_ - (K_pred * np.linalg.inv(K + error) * K_pred.T)
    
    return lc, cov

# -------------------------------------------------------------------
# Abro la curva que quiero samplear

# Ubicacion de las curvas
# 0-1           Be_lc
# 255-256       CEPH
# 457-458       EB
# 967-968       longperiod_lc
# 1697-1698     microlensing_lc
# 2862-2863     non_variables
# 12527-12528   quasar_lc
# 12645-12646   RRL

paths = lu.get_lightcurve_paths()

# a, b = 103, 104
a, b = 197, 11
azul = lu.open_lightcurve(paths[a])
roja = lu.open_lightcurve(paths[b])

azul = lu.filter_data(azul)
roja = lu.filter_data(roja)


# -------------------------------------------------------------------
# Preparo la informacion necesaria

# Array con los tiempos de medicion normalizados
t_obs = np.array(azul.index.reshape(len(azul.index),1))
t_obs = (t_obs - np.mean(t_obs)) / np.std(t_obs)

# Obtengo el tiempo que voy a cortar la curva
aux = t_obs[-1] - t_obs[600]

azul2 = azul
azul = azul.iloc[0:600]

# Array con los tiempos de medicion normalizados
t_obs = np.array(azul.index.reshape(len(azul.index),1))
media_obs, std_obs = np.mean(t_obs), np.std(t_obs)
t_obs = (t_obs - np.mean(t_obs)) / np.std(t_obs)

# Array con los brillos normalizados
y_obs = azul['mag'].reshape(len(azul.index), 1)
y_obs = (y_obs - np.mean(y_obs)) / np.std(y_obs)

# Array con los errores de las mediciones normalizados segun las observaciones
# No tiene sentido centrar los errores
err_obs = azul['err'].reshape(len(azul.index), 1)
err_obs = err_obs / azul['mag'].std()

# quito un numero de puntos
#t_obs = t_obs[0:600]
#y_obs = y_obs[0:600]
#err_obs = err_obs[0:600]

min_time = np.min(t_obs)
max_time = np.max(t_obs)

# Tomo una muestra aleatoria de puntos de la curva
random.seed(3)
n_sampled_points = 100
rand_indices = random.sample(range(0,np.max(np.shape(t_obs))),n_sampled_points)
rand_indices.sort()

t_obs = t_obs[rand_indices]
y_obs = y_obs[rand_indices]
err_obs = err_obs[rand_indices]

# Transformo a matriz
t_obs = np.asmatrix(t_obs)
y_obs = np.asmatrix(y_obs)
err_obs = np.asmatrix(err_obs)

# ------------------------------------------------------------------- 
from sklearn.gaussian_process import GaussianProcess

dy = np.ravel(err_obs.T)

X = t_obs
y = np.ravel(y_obs.T)
nuggets = (dy/y)**2

# Mesh the input space for evaluations of the real function, the prediction and its MSE
# Instanciate a Gaussian Process model
gp = GaussianProcess(corr='squared_exponential', theta0=1e-1,
                     thetaL=1e-3, thetaU=1000,
                     nugget=nuggets,
                     random_start=100)

# Fit to data using Maximum Likelihood Estimation of the parameters
gp = gp.fit(X, y)
print gp.theta_

# ------------------------------------------------------------------- 
# Make the prediction on the meshed x-axis (ask for MSE as well)

num_locs = n_sampled_points
extra_time = aux

x_pred = np.asmatrix(np.linspace(min_time,max_time + extra_time,num_locs)).T
y_pred, MSE = gp.predict(x_pred, eval_MSE=True)
sigma = np.sqrt(MSE)


# ------------------------------------------------------------------- 
# 

L = gp.theta_
k = lambda x,y:np.exp( -L*((x-y)**2) )
lc, cov = sample_LC(X, y, k, (dy/y)**2, x_pred)

np.random.seed(1)

values = []

for i in xrange(100):
    mag = np.random.multivariate_normal(np.ones(num_locs)*lc, cov)
    #values.append(ft.stetsonK(mag, sigma))
    #values.append(ft.period(mag, x_pred))
    # values.append(ft.var_index(mag))
    # values.append(ft.con(mag))
    #values.append(ft.median_abs_dev(mag))

    # values.append(ft.cu_sum(mag))
    values.append(ft.eta(mag))
    
    # values.append(ft.small_kurtosis(mag))
    
    # df = {'mag': mag.tolist()}
    # indice = (np.ravel(x_pred) * std_obs + media_obs).tolist()
    # df = pd.DataFrame(df, index=indice)
    # values.append(ft.slotted_autocorrelation(df))


# real = ft.stetsonK(azul2['mag'].tolist(), azul2['err'].tolist())

# naive = ft.stetsonK(azul['mag'].tolist(), azul['err'].tolist())
#naive = ft.period(y_obs, t_obs)
# naive = ft.slotted_autocorrelation(azul)

# real = ft.con(azul2['mag'].tolist())
# naive = ft.con(azul['mag'].tolist())

# real = ft.median_abs_dev(azul2['mag'].tolist())
# naive = ft.median_abs_dev(azul['mag'].tolist())

# real = ft.var_index(azul2['mag'].tolist())
# naive = ft.var_index(azul['mag'].tolist())

# real = ft.small_kurtosis(azul2['mag'].tolist())
# naive = ft.small_kurtosis(azul['mag'].tolist())


# azul2 = lu.open_lightcurve(paths[a])

# real = ft.cu_sum(azul2['mag'].tolist())
# naive = ft.cu_sum(azul['mag'].tolist())

real = ft.eta(azul2['mag'].tolist())
naive = ft.eta(azul['mag'].tolist())

# real = ft.slotted_autocorrelation(azul2)


t_obs = np.array(azul2.index.reshape(len(azul2.index),1))
t_obs = (t_obs - np.mean(t_obs)) / np.std(t_obs)
y_obs = azul2['mag'].reshape(len(azul2.index), 1)
y_obs = (y_obs - np.mean(y_obs)) / np.std(y_obs)

real = ft.period(y_obs, t_obs)


from gp_hist import graf_hist
graf_hist(values, real, naive, 'Eta')
