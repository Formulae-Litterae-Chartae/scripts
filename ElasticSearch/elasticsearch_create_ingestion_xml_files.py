from glob import glob
import subprocess
from multiprocessing import Pool
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# When rebuilding for the open corpus
# corpus = 'formulae-open'
# When rebuilding for the full corpus
corpus = 'formulae'
# When building test files for new corpora
# corpus = 'corpus_transform'

xmls = [x for x in glob('/home/matt/results/{}/data/*/*/*lat*.xml'.format(corpus)) if 'elexicon' not in x]

def extract_text(xml_file):
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(xml_file), os.path.join(basedir, 'extract_text_search_to_xml.xsl'), '-o:/home/matt/results/{}/search/{}'.format(corpus, xml_file.split('/')[-1].replace('xml', 'txt'))])

if __name__ == '__main__':
    with Pool(processes=3) as pool:
        pool.map(extract_text, xmls)
