# coding=utf-8

# Toma un directorio con training sets y un directorio objetivo
# Agrupo todas las clases que no son ceph o rrlyr en un solo grupo

# -----------------------------------------------------------------------------

import os
import sys
import argparse

import pandas as pd


def filter_class(lc_class):
    cepheids = ['CEPH', 'Ceph_10', 'Ceph_10_20', 'Ceph_F', 'T2CEPH', 'cep',
                't2cep']
    rrlyr = ['RRL', 'rrlyr']

    if lc_class in cepheids:
        return 'ceph'

    elif lc_class in rrlyr:
        return 'rrlyr'
    else:
        return 'other'

if __name__ == '__main__':
    
    print ' '.join(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('--datasets_dir', required=True, type=str)
    parser.add_argument('--result_dir', required=True, type=str)
    
    args = parser.parse_args(sys.argv[1:])

    datasets_dir = args.datasets_dir
    result_dir = args.result_dir

    files = [f for f in os.listdir(datasets_dir) if os.path.isfile(os.path.join(datasets_dir, f))]

    for f in files:
        df = pd.read_csv(os.path.join(datasets_dir, f), index_col=0)

        df['class'] = df['class'].apply(filter_class)

        df.to_csv(result_dir + f)