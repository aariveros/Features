# coding=utf-8

import FATS
import pickle
import pandas as pd
import lightcurves.lc_utils as lu

def calc_sample_feats(t_obs, sample, feature_list=None, exclude_list=None):
    """Metodo ocupado para paralelizar el calculo de las features en el cluster

    feature_list: lista con los nombres de las features que se desea calcular
    t_obs:        Instantes correspondientes a las observaciones de la muestra 
                  se entregan por separado por que son los mismos para todas
    sample:       Tupla con los valores de brillo y los errores asociados para 
                  una curva
    """
    y_obs = sample[0]
    err_obs = sample[1]

    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)
        
    fs = fs.calculateFeature([y_obs, t_obs, err_obs])
    result = map(lambda x: float("{0:.6f}".format(x)), fs.result().tolist())
    del fs

    return result

def calc_feats(lc_path, feature_list=None, exclude_list=None, percentage=1.0, catalog=''):
    """
    """

    macho_id = lu.get_lightcurve_id(lc_path, catalog=catalog)
    macho_class = lu.get_lightcurve_class(lc_path, catalog=catalog)

    f = open(lc_path, 'rb')
    lc = pickle.load(f)
    f.close()

    t_obs = lc[0].tolist()
    y_obs = lc[1].tolist()
    err_obs = lc[2].tolist()

    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)
        
    fs = fs.calculateFeature([y_obs, t_obs, err_obs])
    result = map(lambda x: float("{0:.6f}".format(x)), fs.result().tolist())
    del fs

    return [macho_id] + result + [macho_class]
