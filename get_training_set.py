import lightcurves.lc_utils as lu
import lightcurves.lc_stats as st
import pandas as pd
import os


def get_training_set(path):

    # Abro el directorio y obtengo el nombre de todos los archivos
    archivos = []
    for dirpath,_,filenames in os.walk(path):
       for f in filenames:
            if '.txt' in f:
                archivos.append(os.path.abspath(os.path.join(dirpath, f)))
    
    # Obtengo el header con las features de los datos
    with open(archivos[0], 'r') as f:
        header = f.readline().strip()
    f.close()

    # Agrego los comp al header
    aux = []
    for f in header.split(' '):
        if f != '#Punto':
            aux.append(f)
            aux.append(f + '_comp')
    header = ' '.join(aux)

    # Agrego el label y el macho_id
    header = 'Macho_id ' + header + ' class'


    """ Aqui itero para cada porcentaje"""

    porcentajes = [20, 40, 60, 80, 100]

    for p in porcentajes:

        print 'Generando training set con ' + str(p) + '% de las curvas'

        # Lista de lineas a escribir en el archivo final
        lineas = []
        lineas.append(header)

        # Para cada archivo
        for a in archivos:

            linea = []

            # Agrego el macho_id de la curva
            linea.append(lu.get_lightcurve_id(a))

            # Armo un dataframe con los valores de las features en el tiempo
            df = pd.read_csv(a, sep=" ", index_col=0)

            # print lu.get_lightcurve_id(a)
            # print len(df.index)

            # Para cada feature 
            for c in df.columns:
                serie = df[c]

                # Obtengo el porcentaje de la curva que voy a considerar
                total = len(serie.index)
                parcial = int(total*p/100) - 1

                # calculo su completitud y guardo el valor de la feature en el mismo punto
                valor_feature = serie.iloc[parcial]

                # confianza = st.var_completeness(serie[0:parcial].tolist())
                # confianza = st.completeness(serie[0:parcial].tolist())
                # confianza = st.trust(serie[0:parcial].tolist())
                confianza = st.new_var(serie[0:parcial].tolist())
                
                linea.append(str(valor_feature))
                linea.append(str(confianza))

            # Obtengo el label y agrego la linea a la lista de lineas
            linea.append(str(lu.get_lc_class(a)))
            lineas.append(' '.join(linea))

        # Escribo el set de entrenamiento en un archivo
        with open(RESULTS_DIR_PATH + 'Entrenamiento ' + str(p) + '.txt', 'w') as f:
            for linea in lineas:
                f.write(linea + '\n')
        f.close()


if __name__ == '__main__':
    
    RESULTS_DIR_PATH = '/Users/npcastro/workspace/Features/Entrenamiento var_comp/'
    # RESULTS_DIR_PATH = '/Users/npcastro/workspace/Features/Entrenamiento new_var/'
    path = '/Users/npcastro/workspace/Features/Feature Progress'
    get_training_set(path)