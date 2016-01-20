# coding=utf-8

# Guardo métodos generales de visualización
# -----------------------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import numpy as np


def graf_GP(x, mu, std):
    plt.plot(x, mu, color="#4682b4", alpha=0.3)
    plt.fill(np.concatenate([x, x[::-1]]), \
            np.concatenate([mu - 1.9600 * std,
                           (mu + 1.9600 * std)[::-1]]), \
            alpha=.5, fc='#C0C0C0', ec='None', label='95% confidence interval')

def graf_hist(values, real_value, label):
    std = np.std(values)
    # mean = np.mean(values)
    # x = np.linspace(mean - 4 * std, mean + 4 * std, 100)
    # plt.plot(x, mlab.normpdf(x, mean, std), 'k--')

    n, bins, patches = plt.hist(values, 60, normed=False, histtype='bar', alpha=0.6,
                                label=label + "%0.4f" % std)

    plt.legend()
