from glob import glob
import os

docx = [x for x in glob("/media/FORMAKAD/Werkstatt/e-Lexikon/Freigabe/*.docx") if '~' not in x]

for doc in docx:
    entry_name = doc.lower().split('/')[-1].replace('.docx', '').split('-')
    for name in entry_name:
        print(name)
        output = '/home/matt/results/oxgarage_results/elex/{}.xml'.format(name)
        os.system('curl -s -o "{out}" -F upload=@"{input}" http://localhost:8080/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=doc))
