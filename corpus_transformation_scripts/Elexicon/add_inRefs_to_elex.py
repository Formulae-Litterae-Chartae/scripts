from lxml.builder import ElementMaker
from lxml import etree
from glob import glob
import os
import sys
from json import load

home_dir = os.environ.get('HOME', '')
dest = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(home_dir, 'formulae-corpora') 
basedir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(basedir, 'formulae_elexicon_mapping.json')) as f:
    form_elex_mapping = load(f)

elex_md_files = glob(os.path.join(dest, 'data/elexicon/*/__capitains__.xml'))

ns = {"ti": "http://chs.harvard.edu/xmlns/cts", "dct": "http://purl.org/dc/terms/", "dc": "http://purl.org/dc/elements/1.1/", "cpt": "http://purl.org/capitains/ns/1.0#", "owl": "http://www.w3.org/2002/07/owl#", "bib": "http://bibliotek-o.org/1.0/ontology/", "cts": "http://chs.harvard.edu/xmlns/cts", "foaf": "http://xmlns.com/foaf/0.1/"}

E = ElementMaker(namespace=ns['dct'] , nsmap=ns)
        
for filename in elex_md_files:
    key = filename.split('/')[-2]
    if key not in form_elex_mapping:
        continue                                 
    xml = etree.parse(filename)                                                             
    for readable in xml.xpath('/cpt:collection/cpt:members/cpt:collection[@readable="true"]', namespaces=ns):
        md = readable.xpath('cpt:structured-metadata', namespaces=ns)[0]
        for ref, cit in form_elex_mapping[key].items():
            md.append(E.isReferencedBy('%' + ref + '%' + '%'.join(cit)))
    xml.write(filename, encoding='utf-8', pretty_print=True)
