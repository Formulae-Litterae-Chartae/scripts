from glob import glob
import os
from sys import argv 

docx_folder = argv[1]

docx = [x for x in glob(os.path.join(docx_folder, "*.docx")) if '~' not in x]
os.makedirs(os.path.join(docx_folder, 'oxgarage_results'), exist_ok=True)

for doc in docx:
    entry_name = doc.split('/')[-1].replace('.docx', '')
    new_name = doc.replace(',', '-')
    os.rename(doc, new_name)
    output = os.path.join(docx_folder, 'oxgarage_results/{}.xml'.format(entry_name.replace('Übersetzung', 'Deutsch').replace('-', ',')))
    print(output)
    os.system('curl -s -o "{out}" -F upload=@"{input}" http://localhost:8080/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=new_name))
