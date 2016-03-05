# coding=utf-8

import numpy as np

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