from lxml import etree
from glob import glob
from difflib import get_close_matches
import re
import sys
import os
import subprocess
import argparse
import logging
from pathlib import Path

home_dir = os.environ.get('HOME', '')

parser=argparse.ArgumentParser(description="Script to transform CTE-XML files to ???")
default_saxon_location = home_dir + '/Downloads/SaxonHE10-1J/saxon-he-10.1.jar'
parser.add_argument("orig", type=str,default=default_saxon_location)
parser.add_argument("saxon_location", type=str,default=default_saxon_location)

current_dir = os.path.abspath(os.path.dirname(__file__))
add_bibl_xslt_default = current_dir + "/Formulae/add_missing_bibl_links.xsl"

#parser.add_argument("add_bibl_xslt", type=str, default=default_saxon_location, help="Location of add_missing_bibl_links.xsl")
default_scripts_folder = home_dir + '/scripts'

parser.add_argument("scripts_folder", type=str, default=default_scripts_folder, 
                    help='Path to your local copy of https://github.com/Formulae-Litterae-Chartae/scripts')
args=parser.parse_args()

logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                    encoding='utf-8', datefmt='%H:%M:%S')
# TODO: set the level via cl argument
logging.getLogger().setLevel('DEBUG')


home_dir = os.environ.get('HOME', '')
#orig = str(sys.argv[1])
orig = args.orig

#saxon_location = sys.argv[2]
saxon_location = args.saxon_location


scripts_folder = args.scripts_folder
add_bibl_xslt = scripts_folder+"/corpus_transformation_scripts/Formulae/add_missing_bibl_links.xsl"

kurz = [re.sub('[„“"\'’]', '', x) for x in etree.parse(scripts_folder + '/bibliography/formulae_bibliographie.xml').xpath('//tei:title[@type="short"]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

texts = [x for x in glob(orig + '/data/**/*.xml', recursive=True) if '__capitains__' not in x]

problems = []

for text in sorted(texts):
    for title in etree.parse(text).xpath('//tei:bibl', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        whole_title = ''.join(title.xpath('.//text()'))
        if re.sub('[„“"\'’]', '', whole_title.strip()) not in kurz:
            closest = get_close_matches(whole_title, kurz, n=1, cutoff=0.8)          
            print(text, re.sub('[„“"\'’]', '', whole_title.strip()), closest)                                                       
            problems.append((text.split('/')[-1], whole_title, closest[0] if closest else 'FEHLT'))
        elif title.get('n').strip() in ('', ','):
            subprocess.run(['java', '-jar',  saxon_location, '{}'.format(text), add_bibl_xslt, '-o:{}'.format(text)])
            


problem_path_location = Path(scripts_folder+'/results/elex_problems.txt')


with open(problem_path_location, mode="w+") as f:
    f.write('\n'.join(['\t'.join(x) for x in problems]))

if 0 == len(problems):
    logging.info('No problems detected in '+orig)
else:
    logging.warning('{} problems detected in {}. Please the error log at {}'.format(len(problems),orig, problem_path_location))