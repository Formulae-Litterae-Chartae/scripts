from glob import glob
import re
import subprocess
from json import load
from lxml.builder import ElementMaker
import os

basedir = os.path.abspath(os.path.dirname(__file__))

lexes = glob('/home/matt/results/oxgarage_results/elex/*.xml')
with open(os.path.join(basedir, 'formulae_elexicon_mapping.json')) as f:
    form_elex_mapping = load(f)
ns = {'ti': "http://chs.harvard.edu/xmlns/cts", 'dct': "http://purl.org/dc/terms/", 'cpt': "http://purl.org/capitains/ns/1.0#", 'dc': "http://purl.org/dc/elements/1.1/"}
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
    md = xml.xpath('/ti:work/ti:edition/cpt:structured-metadata', namespaces=ns)[0]
    for ref, cit in form_elex_mapping[key].items():
        md.append(E.isReferencedBy(ref + '%' + '%'.join(cit)))
    xml.write(filename, encoding='utf-8', pretty_print=True)

for lex in lexes:
    entry_name = lex.split('/')[-1].replace('.xml', '').replace('-', '').replace('  ', ' ').replace(' ', '_').lower()
    # I need to figure out if it makes sense to automate copying entries that have two terms to the second file automatically
    new_name = '/home/matt/results/formulae/data/elexicon/{entry}/elexicon.{entry}.deu001.xml'.format(entry=entry_name)
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(lex), os.path.join(basedir, 'transform_elex_to_dll.xsl'), '-o:{}'.format(new_name)])
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(new_name), os.path.join(basedir, 'create_cts_files_elex.xsl'), '-o:/home/matt/results/formulae/data/elexicon/{entry}/__cts__.xml'.format(entry=entry_name)])
    add_inRefs_to_cts('/home/matt/results/formulae/data/elexicon/{entry}/__cts__.xml'.format(entry=entry_name))
    try:
        remove_space_before_note(new_name)
    except FileNotFoundError:
        continue
