from glob import glob
import re
import subprocess
from json import load
from lxml.builder import ElementMaker
import os
from lxml import etree
import sys

home_dir = os.environ.get('HOME', '')
dest = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(home_dir, 'formulae-corpora') 
saxon_path = str(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(home_dir, 'Downloads/SaxonHE9-8-0-11J/saxon9he.jar') # The path to the Saxon JAR file

basedir = os.path.abspath(os.path.dirname(__file__))

lexes = glob('/home/matt/results/oxgarage_results/elex/*.xml')
with open(os.path.join(basedir, 'formulae_elexicon_mapping.json')) as f:
    form_elex_mapping = load(f)
ns = {"ti": "http://chs.harvard.edu/xmlns/cts", "dct": "http://purl.org/dc/terms/", "dc": "http://purl.org/dc/elements/1.1/", "cpt": "http://purl.org/capitains/ns/1.0#", "owl": "http://www.w3.org/2002/07/owl#", "bib": "http://bibliotek-o.org/1.0/ontology/", "cts": "http://chs.harvard.edu/xmlns/cts", "foaf": "http://xmlns.com/foaf/0.1/"}
E = ElementMaker(namespace=ns['dct'] , nsmap=ns)

def remove_space_before_note(filename):
    with open(filename) as f:
        text = f.read()
    text = re.sub(r'\s+<note', '<note', text)
    with open(filename, mode="w") as f:
        f.write(text)
        
def add_inRefs_to_cts(filename):   
    key = filename.split('/')[-2]
    if key not in form_elex_mapping:
        return                                                 
    xml = etree.parse(filename)                                                             
    for readable in xml.xpath('/cpt:collection/cpt:members/cpt:collection[@readable="true"]', namespaces=ns):
        md = readable.xpath('cpt:structured-metadata', namespaces=ns)[0]
        for ref, cit in form_elex_mapping[key].items():
            md.append(E.isReferencedBy('%' + ref + '%' + '%'.join(cit)))
    xml.write(filename, encoding='utf-8', pretty_print=True)

for lex in lexes:
    entry_name = lex.split('/')[-1].replace('.xml', '').replace('-', '').replace('  ', ' ').replace(' ', '_').lower()
    # I need to figure out if it makes sense to automate copying entries that have two terms to the second file automatically
    new_name = dest + '/data/elexicon/{entry}/elexicon.{entry}.deu001.xml'.format(entry=entry_name)
    subprocess.run(['java', '-jar',  saxon_path, '{}'.format(lex), os.path.join(basedir, 'transform_elex_to_dll.xsl'), '-o:{}'.format(new_name)])
    subprocess.run(['java', '-jar',  saxon_path, '{}'.format(new_name), os.path.join(basedir, 'create_capitains_files_elex.xsl'), '-o:{dest}/data/elexicon/{entry}/__capitains__.xml'.format(dest=dest, entry=entry_name)])
    add_inRefs_to_cts('{dest}/data/elexicon/{entry}/__capitains__.xml'.format(dest=dest, entry=entry_name))
    try:
        remove_space_before_note(new_name)
    except FileNotFoundError:
        continue

subprocess.run(['java', '-jar',  saxon_path, '{dest}/data/elexicon/__capitains__.xml'.format(dest=dest), os.path.join(basedir, '../create_textgroup_capitains_files.xsl'), '-o:{dest}/data/elexicon/__capitains__.xml'.format(dest=dest)])
