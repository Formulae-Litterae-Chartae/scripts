from collections import defaultdict
from glob import glob
from lxml import etree
import json

files = glob('/home/matt/formulae-corpora/data/**/*.xml', recursive=True)
types_all_charters = defaultdict(dict)

for file in files:
    xml = etree.parse(file)
    file_dict = defaultdict(list)
    for s in xml.xpath('//tei:seg[@function]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        file_dict[s.get('function')].append(' '.join([x.text for x in s.xpath('.//tei:w', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]))
    for k, v in file_dict.items():
        types_all_charters[k][file] = v

with open('/home/matt/results/corpus_segmentation/parts_from_xmls.json', mode="w") as f:
    json.dump(types_all_charters, f, ensure_ascii=False, indent='\t')
