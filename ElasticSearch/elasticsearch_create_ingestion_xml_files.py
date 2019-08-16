from glob import glob
import subprocess
from multiprocessing import Pool
import os
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
home_dir = os.environ.get('HOME', '')
work_dir = os.environ.get('WORK', home_dir)

# When rebuilding for the open corpus
# corpus = 'formulae-open'
# When rebuilding for the full corpus
orig = str(sys.argv[1]) if len(sys.argv) > 1 else 'results/formulae' # The folder in the home directory where the source files are location and where the search txt files will be saved
# When building test files for new corpora
# corpus = 'corpus_transform'
procs = int(sys.argv[2]) if len(sys.argv) == 3 else 3

xmls = [x for x in glob(os.path.join(work_dir, orig, 'data/*/*/*lat*.xml')) if 'elexicon' not in x]

def extract_text(xml_file):
    subprocess.run(['java', '-jar',  os.path.join(home_dir, 'Downloads/SaxonHE9-8-0-11J/saxon9he.jar'), '{}'.format(xml_file), os.path.join(basedir, 'extract_text_search_to_xml.xsl'), '-o:{}'.format(os.path.join(word_dir, orig, 'search', xml_file.split('/')[-1].replace('xml', 'txt')))])

if __name__ == '__main__':
    with Pool(processes=procs) as pool:
        pool.map(extract_text, xmls)
