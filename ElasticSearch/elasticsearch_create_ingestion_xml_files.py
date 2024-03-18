from glob import glob
import subprocess
from multiprocessing import Pool
import os
import sys
import re

basedir = os.path.abspath(os.path.dirname(__file__))
home_dir = os.environ.get('HOME', '')
work_dir = os.environ.get('WORK', home_dir)

# When rebuilding for the open corpus
# corpus = 'formulae-open'
# When rebuilding for the full corpus
orig = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(work_dir, 'results/formulae') # The folder in the home directory where the source files are location and where the search txt files will be saved
# When building test files for new corpora
# corpus = 'corpus_transform'
saxon_path = str(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(home_dir, 'Downloads/SaxonHE9-8-0-11J/saxon9he.jar') # The path to the Saxon JAR file
corpus_name = str(sys.argv[3]) if len(sys.argv) > 3 else 'all'
procs = int(sys.argv[4]) if len(sys.argv) == 5 else 3


with open(os.path.join(orig, 'data/manuscript_collection/__capitains__.xml')) as manuscript_file:
    manuscript_string = manuscript_file.read()
    manuscript_list = ['data/{}'.format(x[1]) for x in re.finditer('identifier="urn:cts:formulae:([^"]+)"', manuscript_string)]
pattern = re.compile(r'{}'.format('|'.join(manuscript_list)))

if corpus_name == 'all':
    # The following rebuilds the files for all corpora. NB this will probably take several hours to complete.
    xmls = [x for x in glob(os.path.join(orig, 'data/**/*lat*.xml'), recursive=True) if not re.search(pattern, x)] + [x for x in glob(os.path.join(orig, 'data/elexicon/*/*deu001.xml'), recursive=True)]
elif corpus_name == 'elexicon':
    # The following processes all the files for the elexicon
    xmls = [x for x in glob(os.path.join(orig, 'data/elexicon/*/*deu001.xml'), recursive=True) if re.search(r'elexicon', x)]
else:
    # The following processes a single charter or formulae corpus
    xmls = [x for x in glob(os.path.join(orig, 'data/{}/**/*lat*.xml'.format(corpus_name)), recursive=True)]
    if xmls == []:
        raise Exception('Corpus ' + corpus_name + ' does not exist')

def extract_text(xml_file):
    subprocess.run(['java', '-jar',  saxon_path, '{}'.format(xml_file), os.path.join(basedir, 'extract_text_search_to_xml.xsl'), '-o:{}'.format(os.path.join(work_dir, orig, 'search', xml_file.split('/')[-1].replace('xml', 'txt')))])

if __name__ == '__main__':
    with Pool(processes=procs) as pool:
        pool.map(extract_text, xmls)
