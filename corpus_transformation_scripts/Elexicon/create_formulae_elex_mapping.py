from glob import glob
from lxml import etree
from collections import defaultdict
from json import dump
import os

basedir = os.path.abspath(os.path.dirname(__file__))

forms = sorted(glob('/home/matt/results/formulae/data/andecavensis/*/*lat001.xml'))
ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
mapping = defaultdict(dict)

for form in forms:
    xml = etree.parse(form)
    urn = 'urn:cts:formulae:' + form.split('/')[-1].replace('.xml', '')
    for ref in xml.xpath('//tei:w[@lemmaRef]', namespaces=ns):
        elex = ref.get('lemmaRef')
        context = ref.xpath('preceding-sibling::*[descendant-or-self::tei:w]', namespaces=ns)[-2:] + [ref] + ref.xpath('following-sibling::*[descendant-or-self::tei:w]', namespaces=ns)[:2]
        if prev_ref in context:
            continue
        context_str = ''
        for c in context:
            if c == ref:
                context_str += '<span class="elex-word">{}</span>{}'.format(' '.join(c.xpath('.//text()')), c.tail if c.tail else ' ')
            else:
                context_str += ''.join([' '.join(c.xpath('.//text()')), c.tail if c.tail else ' '])
        if urn in mapping[elex]:
            mapping[elex][urn].append(context_str.strip())
        else:
            mapping[elex][urn] = [context_str.strip()]

with open(os.path.join(basedir, 'formulae_elexicon_mapping_new.json'), mode='w') as f:
    dump(mapping, f)
