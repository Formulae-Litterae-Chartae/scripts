from glob import glob
import subprocess
from multiprocessing import Pool
import os
import sys
import re

basedir = os.path.abspath(os.path.dirname(__file__))
home_dir = os.environ.get('HOME', '')
work_dir = os.environ.get('WORK', home_dir)
pattern = re.compile(r'fu2|ka1|ko2|le1|le3|m4|p3|p8|p10|p12|p12s|p14|p16a|p16b|data/s2|sg2|data/syd|v6|v8|v9|v11|wa1|data/z2')

# When rebuilding for the open corpus
# corpus = 'formulae-open'
# When rebuilding for the full corpus
orig = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(work_dir, 'results/formulae') # The folder in the home directory where the source files are location and where the search txt files will be saved
# When building test files for new corpora
# corpus = 'corpus_transform'
saxon_path = str(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(home_dir, 'Downloads/SaxonHE9-8-0-11J/saxon9he.jar') # The path to the Saxon JAR file
procs = int(sys.argv[3]) if len(sys.argv) == 4 else 3

# xmls = [x for x in glob(os.path.join(orig, 'data/**/*lat*.xml'), recursive=True) if not re.search(pattern, x)] + [x for x in glob(os.path.join(orig, 'data/**/*deu001.xml'), recursive=True) if re.search(r'elexicon', x)]
# Use the following line to process a single corpus
xmls = [x for x in glob(os.path.join(orig, 'data/**/*lat*.xml'), recursive=True) if re.search(r'lothar_2', x)]

def extract_text(xml_file):
    subprocess.run(['java', '-jar',  saxon_path, '{}'.format(xml_file), os.path.join(basedir, 'extract_text_search_to_xml.xsl'), '-o:{}'.format(os.path.join(work_dir, orig, 'search', xml_file.split('/')[-1].replace('xml', 'txt')))])

if __name__ == '__main__':
    with Pool(processes=procs) as pool:
        pool.map(extract_text, xmls)
