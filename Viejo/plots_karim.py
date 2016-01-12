# Plots para una presentación de Karim

# -----------------------------------------------------------------------------
import matplotlib.pyplot as plt
import pandas as pd

# df = pd.read_csv('/Users/npcastro/Dropbox/Resultados/EROS/Tree/Regular/Metricas/f_score.csv', index_col=0)
df = pd.read_csv('/Users/npcastro/Dropbox/Resultados/MACHO/RF/Metricas/f_score.csv', index_col=0)

# cols = df.columns.tolist()
# cols = ['RRL', 'Ceph_F', 'OSARG_RGB_O', 'EB', 'Ceph_10','SRV_AGB_O',
# 	 	'SRV_AGB_C', 'LPV', 'Mira_AGB_O', 'Ceph_10_20', 'T2CEPH']

cols = ['non_variables', 'CEPH', 'longperiod_lc', 'RRL', 'microlensing_lc',
		'EB', 'Be_lc', 'quasar_lc']

x = df.index.tolist()

# for c in cols:
# 	plt.figure(c)

# 	y = df[c]
# 	plt.plot(x, y, color="#4682b4")

# 	plt.title(c + ' Classification progress')
# 	plt.xlabel('Lightcurve Percentage used (%)')
# 	plt.ylabel('F-Score', rotation=0)
# 	plt.ylim(0.0, 1.0)

# 	plt.show()

plt.figure()
# colors = ['#ff9933', '#0099ff', '#66ff66', '#ff66ff', '#6666ff',
# 		  '#6600ff', '#ccff66', '#66ffcc', '#cc9900', '#00cc99',
# 		  '#ff0066']
colors = ['#ff9933', '#66ff66', '#6666ff', '#6600ff',
		  '#ccff66', '#cc9900', '#00cc99', '#ff0066']

for i, c in enumerate(cols):
	y = df[c]
	plt.plot(x, y, color=colors[i], label=c)

	plt.title('MACHO Classification progress')
	plt.xlabel('Lightcurve Percentage used (%)')
	plt.ylabel('F-Score', rotation=0)
	plt.ylim(0.0, 1.0)
	plt.legend(ncol=3, loc=4, borderaxespad=1.0)
	# plt.legend(loc=4)

plt.show()


# ax = plt.gca()
# ax.set_xticks(np.arange(0,6,1))
# label = ax.set_xlabel('Xlabel', fontsize = 9)
# ax.xaxis.set_label_coords(1.05, -0.025)