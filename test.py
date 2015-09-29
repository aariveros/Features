from config import *
from gp_u_set import get_paths

percentage = '100'

path = LAB_PATH + 'Samples_Features/MACHO/' + percentage + '%'

files = get_paths(path)

f = next(files)
df = pd.read_csv(f, dtype='float64')

err_file = open('data_errors ' + percentage + '.txt', 'w')

if df.shape[0] != 100 or df.shape[1] != 23:
	err_file.write(f + '\n')

if df.isnull().values.any():
	err_file.write(f + '\n')