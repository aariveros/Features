# coding=utf-8

# Modelo ocupado con gaussian process. Sacado de uno de los ejemplos en la 
# documentación del paquete George
# -----------------------------------------------------------------------------

import numpy as np
import george
from george import kernels
import emcee

def model(params, t):
    """Implementation of the model
    
    parameters
    ----------
    params:
    t: 
    """
    amp, loc, sig2 = params
    return amp * np.exp(-0.5 * (t - loc) ** 2 / sig2)

def lnprior_base(p):
    """Base of the model prior
    """
    amp, loc, sig2 = p
    if not -10 < amp < 10:
        return -np.inf
    if not -5 < loc < 5:
        return -np.inf
    if not 0 < sig2 < 3.0:
        return -np.inf
    return 0.0

def lnlike_gp(p, t, y, yerr):
    """Computes the log-likelihood of the gaussian process model
    """
    a, tau = np.exp(p[:2])
    gp = george.GP(a * kernels.Matern32Kernel(tau))
    # gp = george.GP(a * kernels.ExpSquaredKernel(tau))
    gp.compute(t, yerr)
    return gp.lnlikelihood(y - model(p[2:], t))

def lnprior_gp(p):
    """Gaussian process prior on the parameters
    """
    lna, lntau = p[:2]
    if not -5 < lna < 5:
        return -np.inf
    if not -5 < lntau < 5:
        return -np.inf
    return lnprior_base(p[2:])

def lnprob_gp(p, t, y, yerr):
    """Combine the prior and the likelihood to get the probabilistic model
    """
    lp = lnprior_gp(p)
    if not np.isfinite(lp):
        return -np.inf
    return lp + lnlike_gp(p, t, y, yerr)

def fit_gp(initial, data, nwalkers=32, verbose=False):
    ndim = len(initial)
    p0 = [np.array(initial) + 1e-8 * np.random.randn(ndim)
          for i in xrange(nwalkers)]
    sampler = emcee.EnsembleSampler(nwalkers, ndim, lnprob_gp, args=data)

    if verbose:
        print("Running burn-in")
    
    p0, lnp, _ = sampler.run_mcmc(p0, 500)
    sampler.reset()

    if verbose:
        print("Running second burn-in")

    p = p0[np.argmax(lnp)]
    p0 = [p + 1e-8 * np.random.randn(ndim) for i in xrange(nwalkers)]
    p0, _, _ = sampler.run_mcmc(p0, 500)
    sampler.reset()

    if verbose:
        print("Running production")
    p0, _, _ = sampler.run_mcmc(p0, 1000)

    return sampler