import pandas as pd
import numpy as np

def discretize_data_frame(df,n_bins):
    for key in df.columns:
        hist, bin_edges = np.histogram(df[key], n_bins)
        df[key] = np.digitize(df[key], bin_edges)
    return df
