import FATS

def calc_features(t_obs, sample, feature_list=None, exclude_list=None):
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
    result = map(lambda x: float("{0:.6f}".format(x)), fs.result(method='dict').values())
    del fs

    return result