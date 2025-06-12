from glob import glob
import os
from sys import argv
import logging
from util import make_proper_path, get_logger
from tqdm import tqdm
import requests

logging = get_logger()

def determine_tei_garage_url() -> str:
    LIST_OF_POSSIBLE_HOSTS = ["http://fdm.awhamburg.de:17107", "http://localhost:8080"]
    for host_url in LIST_OF_POSSIBLE_HOSTS:
        response = requests.get(host_url+'/ege-webservice/Info')
        if response.status_code == 200:
            return host_url
    # none of the host provide a fitting api
    raise ArgumentError('None of the host'+str(LIST_OF_POSSIBLE_HOSTS)+'provide an API')


if len(argv) > 1:
    docx_folder = argv[1]
    if len(argv) > 2:
        tei_garage_url = argv[2]
    else:
        tei_garage_url = determine_tei_garage_url()
else:
    raise ArgumentError('Please set the docx_folder')

docx_folder = make_proper_path(argv[1])

docx = [x for x in glob(os.path.join(docx_folder, "*.docx")) if '~' not in x]
uebersetzung_files = [file_name for file_name in docx if "Übersetzung" in file_name]
os.makedirs(os.path.join(docx_folder, 'oxgarage_results'), exist_ok=True)

if len(docx) < 1: logging.error('No docx-files found in {}. So no files will be transformed.'.format(docx_folder))
if len(docx) > len(uebersetzung_files): logging.warning('Not all docx-files (n={}) contain Übersetzung (n={})'.format(len(docx), len(uebersetzung_files)))

for doc in tqdm(uebersetzung_files):
    entry_name = doc.split('/')[-1].replace('.docx', '')
    new_name = doc.replace(',', '-')
    os.rename(doc, new_name)
    output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format(entry_name.replace('Übersetzung', 'Deutsch').replace('-', ',')))
    logging.info('{}'.format(output))
    os.system('curl -s -o "{out}" -F upload=@"{input}" {url}/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=doc, url=tei_garage_url))
