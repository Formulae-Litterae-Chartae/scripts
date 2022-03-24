from glob import glob
from lxml import etree
import sys

regest_file = sys.argv[1]
collection_folder = sys.argv[2] # e.g. /home/matt/formulae-corpora/data/andecavensis

regesten = etree.parse(regest_file)
files = glob('{}/*/__capitains__.xml'.format(collection_folder))

for f in files:
    xml = etree.parse(f) 
    f_id = xml.xpath('/cpt:collection/cpt:identifier/text()', namespaces={'cpt': 'http://purl.org/capitains/ns/1.0#'})[0] 
    try: 
        regest = regesten.xpath('/xml/regest[@docId="{}"]'.format(f_id))[0] 
    except Exception as E: 
        print(E, f) 
        continue 
    short = ''.join([etree.tostring(x, encoding=str, with_tail=False) if isinstance(x, etree._Element) else x for x in regest.xpath('shortDesc/node()')] ) 
    long_desc = ''.join([etree.tostring(x, encoding=str, with_tail=False) if isinstance(x, etree._Element) else x for x in regest.xpath('longDesc/node()')] ) 
    for d in xml.xpath('/cpt:collection/cpt:members/cpt:collection/dc:description', namespaces={'cpt': 'http://purl.org/capitains/ns/1.0#', 'dc': 'http://purl.org/dc/elements/1.1/'}): 
        d.text = long_desc
    for a in xml.xpath('/cpt:collection/cpt:members/cpt:collection/cpt:structured-metadata/dct:abstract', namespaces={'cpt': 'http://purl.org/capitains/ns/1.0#', 'dct': 'http://purl.org/dc/terms/'}): 
        a.text = short 
    xml.write(f, encoding='utf-8', pretty_print=True)
