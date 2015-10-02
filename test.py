# En este script voy a correr pruebas para revisar la integridad de los archivos 
# De features sampleadas

import sys

import pandas as pd
import FATS

import lightcurves.lc_utils as lu
from config import *
from gp_u_set import get_paths

if len(sys.argv) == 2:
    percentage = sys.argv[1]
else:
    percentage = '100'

fs = FATS.FeatureSpace(Data=['magnitude', 'time', 'error'], featureList=None,
                       excludeList=['Color', 'Eta_color', 'Q31_color',
                                    'StetsonJ','StetsonL', 'CAR_mean',
                                    'CAR_sigma', 'CAR_tau'])
feat_names = fs.featureList
num_feats = len(feat_names)

path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%'
files = get_paths(path)
err_file = open('/n/home09/ncastro/workspace/Features/data_errors/errors_' + percentage + '.txt', 'w')

for f in files:
    df = pd.read_csv(f, dtype='float64')
    
    if df.shape[0] != 100 or df.shape[1] != 22:
        err_file.write(f + ' 1 \n')

    if df.isnull().values.any():
        err_file.write(f + ' 2 \n')

err_file.close()
