from glob import glob
import re
import subprocess
import os

basedir = os.path.abspath(os.path.dirname(__file__))

latins = [x for x in glob('/home/matt/results/formulae/data/*/*/__cts__.xml') if re.search('fulda', x)]

for latin in latins:
    print(latin)
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(latin), os.path.join(basedir, 'recreate_cts_files.xsl'), '-o:{}'.format(latin)])
