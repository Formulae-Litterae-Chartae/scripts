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
import pandas as pd

home_dir = os.environ.get('HOME', '')

parser=argparse.ArgumentParser(description="Script to transform CTE-XML files to ???")
default_saxon_location = home_dir + '/Downloads/SaxonHE10-1J/saxon-he-10.1.jar'
default_orig_location = home_dir + '/git/formulae-corpora/data'
parser.add_argument("orig", type=str, help='Source folder with all the xml-files, you want to check.', default=default_orig_location)
parser.add_argument("saxon_location", type=str, default=default_saxon_location)

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

bibliography_xml_path = scripts_folder + '/bibliography/formulae_bibliographie.xml'

kurztitel_list:list[str] = [re.sub('[„“"\'’]', '', x) for x in etree.parse(bibliography_xml_path).xpath('//tei:title[@type="short"]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

def check_kurztitel(kurztitel_list: list[str], bibliography_xml_path: str, logging) -> bool:
    """
    Checks whether any of the given 'Kurztitel' strings contain unwanted LaTeX encodings.

    These LaTeX encodings may cause downstream processing errors if not removed.
    The function scans for known problematic LaTeX control sequences and logs an error 
    if any are found.

    Parameters:
        kurztitel_list (list[str]): A list of Kurztitel strings to check.
        bibliography_xml_path (str): The path to the bibliography XML file (for logging context).
        logging: A logger instance for error reporting.

    Returns:
        bool: True if no LaTeX encodings were found, False otherwise.
    """
    latex_encodings = ['\\glqq', '\\grqq', '\\S']  # properly escaped backslashes for raw strings
    latex_encodings_found: set[str] = set()

    for kurztitel in kurztitel_list:
        for latex_encoding in latex_encodings:
            if latex_encoding in kurztitel:
                latex_encodings_found.add(latex_encoding)

        if latex_encodings_found:
            logging.error(
                'LaTeX encodings found in {}: {}. '
                'Remove them to avoid errors later.'.format(bibliography_xml_path, ', '.join(set(latex_encodings_found)))
            )
            return False

    return True

check_kurztitel(kurztitel_list, bibliography_xml_path, logging) 

if 'data' in orig:
    glob_str = orig + '/**/*.xml'
else:
    glob_str = orig + '/data/**/*.xml'

texts:list[str] = [x for x in glob(glob_str, recursive=True) if '__capitains__' not in x]

problems:list[tuple] = []

for text in sorted(texts):
    for title in etree.parse(text).xpath('//tei:bibl', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        whole_title = ''.join(title.xpath('.//text()'))
        # ‘
        whole_title_cleaned = re.sub('[„“"\'’‘]', '', whole_title.strip())
        if whole_title_cleaned not in kurztitel_list:
            closest = get_close_matches(whole_title, kurztitel_list, n=1, cutoff=0.8)          
            logging.debug("{} {} {}".format(text, re.sub('[„“"\'’]', '', whole_title.strip()), closest))          
            identifier= text.split('/')[-1]                                              
            problems.append((identifier, whole_title, closest[0] if closest else 'FEHLT'))
            if len(problems) > 1:
                if problems[-1] == problems[-2]:
                    logging.warning('problem duplicate for {}. Maybe indicates an error with the footnotes.'.format(identifier))
        elif title.get('n').strip() in ('', ','):
            subprocess.run(['java', '-jar',  saxon_location, '{}'.format(text), add_bibl_xslt, '-o:{}'.format(text)])

        

problem_path_location = Path(scripts_folder+'/results/elex_problems.txt')


if 0 == len(texts):
    logging.warning('No texts were found in {}. Please change the path'.format(glob_str))
elif 0 == len(problems):
    logging.info('No problems detected in {}. Identified {} texts {} kurz'.format(glob_str, len(texts), len(kurztitel_list)))
else:
    if problems:
        df = pd.DataFrame.from_records(problems)
        df = df.sort_values(by=[0,1]).reset_index(drop = True)
        df.to_csv(problem_path_location, sep='\t')
        df.columns = ['Datei', 'Referenz_in_Datei', 'Referenz_Citavi']
        df.to_excel(os.path.join(scripts_folder, 'results', 'fehlende_kurztitel.xlsx'), index=False) 
    logging.warning('{} problems detected in {}. Please the error log at {}'.format(len(problems),glob_str, problem_path_location))