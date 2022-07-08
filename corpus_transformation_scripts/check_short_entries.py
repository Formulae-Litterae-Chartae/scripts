from lxml import etree
from glob import glob
from difflib import get_close_matches
import re
import sys
import os
import subprocess

orig = str(sys.argv[1])
saxon_location = sys.argv[2]
add_bibl_xslt = "/home/matt/scripts/corpus_transformation_scripts/Formulae/add_missing_bibl_links.xsl"

kurz = [re.sub('[„“"\'’]', '', x) for x in etree.parse('/home/matt/results/Bibliographie_E-Lexikon.xml').xpath('//tei:title[@type="short"]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})]

texts = [x for x in glob(orig + '/data/**/*.xml', recursive=True) if '__capitains__' not in x]

problems = []

for text in sorted(texts):
    for title in etree.parse(text).xpath('//tei:bibl', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        whole_title = ''.join(title.xpath('.//text()'))
        if re.sub('[„“"\'’]', '', whole_title.strip()) not in kurz:
            closest = get_close_matches(whole_title, kurz, n=1, cutoff=0.8)          
            print(text, re.sub('[„“"\'’]', '', whole_title.strip()), closest)                                                       
            problems.append((text.split('/')[-1], whole_title, closest[0] if closest else 'FEHLT'))
        elif title.get('n').strip() in ('', ','):
            subprocess.run(['java', '-jar',  saxon_location, '{}'.format(text), add_bibl_xslt, '-o:{}'.format(text)])
            
            
with open('/home/matt/results/elex_problems.txt', mode="w") as f:                                                                                                                                      
    f.write('\n'.join(['\t'.join(x) for x in problems]))
