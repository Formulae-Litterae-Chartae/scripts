from glob import glob
import os
from sys import argv
import logging
from util import make_proper_path, get_logger


logging = get_logger()
docx_folder = make_proper_path(argv[1])

docx = [x for x in glob(os.path.join(docx_folder, "*.docx")) if '~' not in x]
uebersetzung_files = [file_name for file_name in docx if "Übersetzung" in file_name]
os.makedirs(os.path.join(docx_folder, 'oxgarage_results'), exist_ok=True)

if len(docx) < 1: logging.error('No docx-files found in {}. So no files will be transformed.'.format(docx_folder))
if len(docx) > len(uebersetzung_files): logging.warning('Not all docx-files (n={}) contain Übersetzung (n={})'.format(len(docx), len(uebersetzung_files)))

for doc in uebersetzung_files:
    entry_name = doc.split('/')[-1].replace('.docx', '')
    new_name = doc.replace(',', '-')
    os.rename(doc, new_name)
    output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format(entry_name.replace('Übersetzung', 'Deutsch').replace('-', ',')))
    logging.info('{}'.format(output))
    os.system('curl -s -o "{out}" -F upload=@"{input}" http://localhost:8080/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=new_name))
