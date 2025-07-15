from argparse import ArgumentError
from glob import glob
import os
from sys import argv 



if len(argv) > 1:
    docx_folder = argv[1]
    if len(argv) > 2:
        # e.g., http://fdm.awhamburg.de:17107
        tei_garage_url = argv[2]
    else:
        tei_garage_url = "http://localhost:8080/"
else:
    raise ArgumentError('Please set the docx_folder')

docx = [x for x in glob(os.path.join(docx_folder, "*.docx")) if '~' not in x]
os.makedirs(os.path.join(docx_folder, 'oxgarage_results'), exist_ok=True)




for doc in docx:
    entry_name = doc.lower().split('/')[-1].replace('.docx', '')
    
    
    if entry_name == 'natio - gens':

        output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format('natio'))
        print(entry_name, '->', output)

        output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format('gens'))
        print(entry_name, '->', output)
    else:
        output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format(entry_name.replace('übersetzung', '')))
        print(entry_name, '->', output)
        if '-' in entry_name or '_' in entry_name:
            print(entry_name+' looks like an entry with two titles. Consider creating a duplicate as done for servus-acila')
    os.system('curl -s -o "{out}" -F upload=@"{input}" {url}/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=doc, url=tei_garage_url))
