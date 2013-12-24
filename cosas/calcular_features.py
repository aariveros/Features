import math
import pandas as pd
import numpy as np
import os

def feature_func(path, class_label, output_file):
    cols = ['mjd', 'mag', 'err']
    data = pd.read_table(path, skiprows = [0,1,2], names = cols, index_col = 'mjd', sep = '\s+')
    num_bins = 32
    entropies = []
    while num_bins > 1:
        histogram = np.histogram(data.mag, num_bins)
        total = np.float64(sum(histogram[0]))
        freqs = np.array(map(np.float64, histogram[0]))
        probs = map(lambda x: x/total, freqs)
        entropy = 0
        for p in probs:
            if p > 0:
                entropy += p*math.log(p, 2)
        entropy = (-1)*entropy
        entropies.append(entropy)
        num_bins = num_bins/2
    line = ' '.join(map(str, entropies)) + ' ' + str(class_label)
    print line
    output_file.write(line + '\n')

def calcular_features(root_dir, output_path, ext, class_label):
    output_file = open(output_path, 'a')
    for i in os.listdir(root_dir):
        if i.endswith(ext):
            feature_func(root_dir+i, class_label, output_file)

