# coding=utf-8

# Metodos útiles para optimizar GP
# -----------------------------------------------------------------------------

from functools import partial

import scipy.optimize as op
import numpy as np
import george

# Defino la función objetivo (negative log-likelihood in this case).
def nll(p, gp=None, y_obs=None):
        """
        gp: objeto de gaussian process
        y: observaciones sobre las que se ajusta el modelo
        p: parametros sobre los que se quiere optimizar el modelo
        """
        # Update the kernel parameters and compute the likelihood.
        gp.kernel[:] = p
        ll = gp.lnlikelihood(y_obs, quiet=True)

        # The scipy optimizer doesn't play well with infinities.
        return -ll if np.isfinite(ll) else 1e25

# Gradiente de la función objetivo. Se ocupa para algunos métodos de optimización
def grad_nll(p, gp=None, y_obs=None):
    # Update the kernel parameters and compute the likelihood.
    gp.kernel[:] = p
    return -gp.grad_lnlikelihood(y_obs, quiet=True)

def find_best_fit(kernel, t_obs, y_obs, err_obs):
    gp = george.GP(kernel, mean=np.mean(y_obs))
    gp.compute(t_obs, yerr=err_obs)
    partial_op = partial(nll, gp=gp, y_obs=y_obs)
    p0 = gp.kernel.vector
    results = op.minimize(partial_op, p0,  method='Nelder-Mead')
    gp.kernel[:] = results.x
    return gp.kernel