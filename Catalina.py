import pandas as pd

path = '/Users/npcastro/Lab/Catalina/AllVar.phot'
index_path = '/Users/npcastro/Lab/Catalina/CatalinaVars.dat'
classes_names_path = '/Users/npcastro/Lab/Catalina/Classes.csv'

cols = ['CAT_ID', 'mjd', 'mag', 'err', 'rad', 'dec']
data = pd.read_csv(path, names=cols, index_col='CAT_ID', sep=',')

cols = ['Catalina_Surveys_ID' ,'Numerical_ID' ,'RA_(J2000)','Dec','V_(mag)', 'Period_(days)', 'Amplitude', 'Number_Obs','Var_Type']
a = pd.read_csv(index_path, names=cols, sep='\s+', skiprows=1, index_col='Numerical_ID')
a = a[['Var_Type']]

b = pd.read_csv(classes_names_path, header=0, sep='\s+', index_col='Class_number')

c = pd.merge(a, b, how='inner', left_on='Var_Type', right_index=True)

d = data.groupby(level=0)

count = 0
for lc_id, lc in d:
	print str(count) + ' Curva id: ' + str(lc_id)
	count += 1
	
	lc = lc.drop(['rad', 'dec'], axis=1)

	clase = c.loc[lc_id]['Class_name']

	lc = lc.set_index('mjd')

	lc.to_csv('/Users/npcastro/Lab/Catalina_lcs/' + clase + '/' + 'CAT_' + str(lc_id) + '.csv')