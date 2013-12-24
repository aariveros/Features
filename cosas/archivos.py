"""
La idea es recibir un directorio raiz, una extension de archivo y una funcion,
para iterar sobre el directorio recursivamente pasandole el archivo a la funcion.

root = '/Users/cristobal/Documents'
ext = 'txt'
func = una funcion en python

"""
import os
from os.path import join, getsize
for root, dirs, files in os.walk('Dropbox/MSc/bases/lightcurves'):
    print "root: "+root
    print "dirs: "+str(len(dirs))
    print "files: "+str(len(files))
