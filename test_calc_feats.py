# coding=utf-8

# Profiling de gasto de memoria de libreria FATS
# --------------------------------------------------------------------------

import FATS

from config import *

def calc_feature(t_obs, sample, feature_list=None, exclude_list=None):
    fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], 
                           featureList=feature_list, excludeList=exclude_list)

    y_obs = sample[0]
    err_obs = sample[1]

    fs = fs.calculateFeature([y_obs, t_obs, err_obs])
    result = map(lambda x: float("{0:.6f}".format(x)), fs.result(method='dict').values())

    return result

if __name__ == '__main__':
    percentage = '10'
    sample_path = LAB_PATH + 'GP_Samples/MACHO/' + percentage + '%/non_variables/1.3441.2081 samples.pkl'

    feature_list = ['Amplitude', 'AndersonDarling', 'Autocor_length', 'Beyond1Std', 'Con',
                    'Eta_e', 'LinearTrend', 'MaxSlope', 'Mean', 'Meanvariance', 'MedianAbsDev',
                    'MedianBRP', 'PairSlopeTrend', 'PercentAmplitude', 'PercentDifferenceFluxPercentile',
                    'Q31', 'Rcs', 'Skew', 'SlottedA_length', 'SmallKurtosis',
                    'Std', 'StetsonK','StetsonK_AC']

    exclude_list = None

    aux = open(sample_path, 'r')
    samples = pickle.load(aux)
    aux.close()

    t_obs = samples[0]
    sample = samples[1][0]

    res = calc_feature(t_obs, sample, feature_list, exclude_list)