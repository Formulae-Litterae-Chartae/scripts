from glob import glob
from lxml import etree
from collections import defaultdict
from json import dump
import os
import re
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
home_dir = environ.get('HOME', '')
corpus_dir = sys.argv[1] if len(sys.argv) > 1 else home_dir + '/formulae-corpora/'

forms = sorted([x for x in glob(corpus_dir + 'data/**/*.xml', recursive=True) if '__capitains__' not in x])
ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
mapping = defaultdict(dict)
print(corpus_dir)

for form in forms:
    xml = etree.parse(form)
    urn = 'urn:cts:formulae:' + form.split('/')[-1].replace('.xml', '')
    form_title = xml.xpath('/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', namespaces=ns)[0].text or ''
    prev_ref = None
    words = xml.xpath('//tei:w', namespaces=ns)
    for i, ref in enumerate(words):
        if ref.get('lemmaRef'):
            if 'elexicon' in form and ref.get('lemmaRef') in form_title.lower():
                continue
            elex = ref.get('lemmaRef')
            context = words[max(i - 2, 0):min(i + 3, len(words))]
            if elex == "habere_tenere_possidere":
                context = words[max(i - 2, 0):min(i + 7, len(words))]
            if prev_ref in context and prev_ref.get('lemmaRef') == elex:
                prev_ref = ref
                continue
            prev_ref = ref
            context_str = ''
            for c in context:
                if c.get('lemmaRef') == elex:
                    context_str += "<span class='elex-word'>{}</span>{}".format(' '.join(c.xpath('.//text()')), c.tail if c.tail else ' ')
                else:
                    context_str += ''.join([' '.join(c.xpath('.//text()')), c.tail if c.tail else ' '])
            if urn in mapping[elex]:
                mapping[elex][urn].append(context_str.strip())
            else:
                mapping[elex][urn] = [context_str.strip()]

with open(os.path.join(corpus_dir, 'formulae_elexicon_mapping.json'), mode='w') as f:
    dump(mapping, f, ensure_ascii=False, indent='\t')
