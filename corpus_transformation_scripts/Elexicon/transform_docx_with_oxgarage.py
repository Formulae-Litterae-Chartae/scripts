from glob import glob
import os

docx = [x for x in glob("/home/matt/results/corpus_transformation/marculf_II/Deutsch/*.docx") if '~' not in x]

for doc in docx:
    entry_name = doc.lower().split('/')[-1].replace('.docx', '').split('-')
    for name in entry_name:
        output = '/home/matt/results/corpus_transformation/marculf_II/Deutsch/oxgarage_results/{}.xml'.format(name.replace('übersetzung', ''))
        print(output)
        os.system('curl -s -o "{out}" -F upload=@"{input}" http://localhost:8080/ege-webservice/Conversions/docx%3Aapplication%3Avnd.openxmlformats-officedocument.wordprocessingml.document/TEI%3Atext%3Axml/'.format(out=output, input=doc))
