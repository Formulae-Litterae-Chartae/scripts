import os
import re
from glob import glob
from sys import argv
from lxml import etree
import json
from string import punctuation

if len(argv) < 4:
    raise SyntaxError('\nThis script needs 3 arguments: 1) path to corpus folder, 2) path to inflected to lem mapping file, 3) path to output file\n')
corpus_folder = argv[1]
inflected_to_lem_mapping = argv[2]
output_file = argv[3]
if not os.path.isdir(corpus_folder):
    raise SyntaxError('\n**The first argument must be a CapiTainS compatible corpus folder.**\n')
files = [x for x in glob(os.path.join(corpus_folder, '**/*lat00*.xml'), recursive=True) if '__capitains__' not in x]
inflected_forms = ['form\tlemma\tPOS\tmorph']
if os.path.isfile(inflected_to_lem_mapping):
    with open(inflected_to_lem_mapping) as f:
        lem_mapping = json.load(f)

for f in sorted(files):
    inflected_forms.append('**' + os.path.basename(f).replace('.xml', '') + '**') 
    xml = etree.parse(f)
    tokens = xml.xpath('/tei:TEI/tei:text/tei:body/tei:div/tei:div/descendant::*[not(ancestor-or-self::tei:note) and not(ancestor-or-self::tei:locus) and not(ancestor-or-self::tei:title)]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    for i, w in enumerate(tokens):
        if w.strip():
            w = w.strip()
            if w.lower() in lem_mapping:
                if len(lem_mapping[w.lower()]) == 1:
                    inflected_forms.append('{form}\t{lemma}\t\t'.format(form=w, lemma=lem_mapping[w.lower()][0]))
                else:
                    inflected_forms.append('{form}\t!Prüfen\t\t'.format(form=w))
            elif w in punctuation:
                inflected_forms.append('{form}\t{form}\t\t'.format(form=w))
            elif (w == w.title() or w == w.upper()) and re.search(r'us$|um$|i$', w.lower()):
                inflected_forms.append('{form}\tPersonenname\t\t'.format(form=w))
            elif (w == w.title() or w == w.upper()) and i - 2 >= 0 and tokens[i - 2] == 'de':
                inflected_forms.append('{form}\tOrtsname\t\t'.format(form=w))
            else:
                inflected_forms.append('{form}\t!Prüfen\t\t'.format(form=w))

with open(output_file, mode="w") as f:
    f.write('\n'.join(inflected_forms))
