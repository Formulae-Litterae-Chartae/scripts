from lxml import etree
from glob import glob
from difflib import get_close_matches
import re
import sys
import os

orig = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(work_dir, 'results/formulae') 

kurz = [re.sub('[„“"\'’]', '', x) for x in etree.parse('/home/matt/results/Bibliographie_E-Lexikon.xml').xpath('//tei:title[@type="short"]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

texts = [x for x in glob(orig + '/data/**/*.xml', recursive=True) if re.search('andecavensis|elexicon|marculf|auvergne', x) and '__capitains__' not in x]

problems = []

for text in sorted(texts):
    for title in etree.parse(text).xpath('//tei:bibl', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        whole_title = ''.join(title.xpath('.//text()'))
        if re.sub('[„“"\'’]', '', whole_title.strip()) not in kurz:
            closest = get_close_matches(whole_title, kurz, n=1, cutoff=0.8)          
            print(text, whole_title, closest)                                                       
            problems.append((text.split('/')[-1], whole_title, closest[0] if closest else 'FEHLT'))
            
            
with open('/home/matt/results/elex_problems.txt', mode="w") as f:                                                                                                                                      
    f.write('\n'.join(['\t'.join(x) for x in problems]))
