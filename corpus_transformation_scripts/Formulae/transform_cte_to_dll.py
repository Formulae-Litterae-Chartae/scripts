from glob import glob
import re
import subprocess
from os import makedirs, environ, getcwd, remove, rename
import os.path
import sys
from lxml import etree

home_dir = environ.get('HOME', '')
saxon_location = sys.argv[1] or home_dir + '/Downloads/SaxonHE10-1J/saxon-he-10.1.jar'
text_transformation_xslt = home_dir + '/scripts/corpus_transformation_scripts/Formulae/transform_cte_to_dll.xsl'
metadata_transformation_xslt = home_dir + '/scripts/corpus_transformation_scripts/Formulae/create_capitains_files.xsl'
collection_metadata_xslt = home_dir + '/scripts/corpus_transformation_scripts/Formulae/create_collection_capitains_files.xsl'
corpus_name = sys.argv[2] or 'andecavensis' # Used to build the folder structure
destination_folder = getcwd() # The base folder where the corpus folder structure should be built
latins = glob(destination_folder + '/Latin/*.xml')
germans = []#glob(destination_folder + '/Deutsch/*.xml')
transcriptions = glob(destination_folder + '/Transkripte/**/*.xml', recursive=True)
temp_files = []

def remove_space_before_note(filename):
    with open(filename) as f:
        text = f.read()
    text = re.sub(r'\s+<note', '<note', text)
    with open(filename, mode="w") as f:
        f.write(text)
        
def remove_tei_dtd_reference(filename):
    with open(filename) as f:
        text = f.read()
    if "Please register the Classical Text Editor to get more" in text:
        raise ValueError("File not complete.\nNeeds to be re-exported from a registered version of CTE.")
    text = text.replace('<!DOCTYPE TEI PUBLIC "-//TEI//DTD TEI P5//EN" "tei.dtd" >', '')
    # Correct the TEI namespace URL
    text = text.replace('https://www.tei-c.org/ns/1.0', 'http://www.tei-c.org/ns/1.0')
    text = text.replace('<title/>', '<title>{}</title>'.format(filename.split('/')[-1]))
    text = text.replace(': Created by an unregistered copy of the Classical Text Editor.', '')
    with open(filename, mode="w") as f:
        f.write(text)
        
def produce_form_num(filename):
    if 'Weltzeitalter' in filename:
        form_num = 'computus'
    elif 'Capitula' in filename:
        form_num = '0_capitula'
        if 'II' in filename:
            form_num = '2_capitula'
        elif 'I' in filename:
            form_num = '1_capitula'
        elif ' Pa ' in filename:
            form_num = '2_capitula'
        elif ' Ko ' in filename:
            form_num = '3_capitula'
    elif 'Incipit' in filename:
        form_num = '1_incipit'
        if 'II' in filename:
            form_num = '2_incipit'
    elif 'Praefatio' in filename:
        form_num = 'form000'
    elif 'Ergänzung' in filename:
        if re.search(r'mar[ck]ulf', filename):
            form_num = 'form3_'
            if ',' in filename:
                form_num = form_num + re.sub(r'.*(\d),(\d).*', r'\1', filename)
                form_num = form_num + '_{:03}'.format(int(re.sub(r'.*(\d),(\d).*', r'\2', filename)))
            else:
                form_num = 'form3_2_001'
        else:
            form_num = 'form2_' + '{:03}'.format(int(re.sub(r'.*?(\d).*', r'\1', filename)))
    elif 'Tours 40' in filename:
        form_num = 'form040_' + re.sub(r'.*Tours 40\((.)\).*', r'\1', filename)
    else:
        num_match = re.search(r',?([\d]+)(\w?)', filename)
        form_num = "{:03}".format(int(num_match[1])) + num_match[2]
        if re.search('II,|Flavigny Pa ', filename):
            form_num = 'form2_' + form_num
        elif re.search('Flavigny Ko ', filename):
            form_num = 'form3_' + form_num
        elif re.search('I,|Flavigny', filename):
            form_num = 'form1_' + form_num
        else:
            form_num = 'form' + form_num
    return form_num

for german in germans:
    print(german)
    remove_tei_dtd_reference(german)
    form_num = produce_form_num(german)
    new_name = '{base_folder}/data/{corpus}/{form}/{corpus}.{form}.deu001.xml'.format(base_folder=destination_folder, corpus=corpus_name, form=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(german), text_transformation_xslt])
    remove_space_before_note(new_name)
    
for transcription in sorted(transcriptions):
    print(transcription)
    remove_tei_dtd_reference(transcription)
    form_num = produce_form_num(transcription)
    try:
        manuscript = re.search(r'\((\w+)\)\Z', transcription.replace('.xml', '')).group(1).lower()
    except:
        print(transcription)
        raise(AttributeError)
    transcript_folders = glob('{base_folder}/data/{manuscript}/*'.format(base_folder=destination_folder, manuscript=manuscript))
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(transcription), text_transformation_xslt])
    new_file = glob(destination_folder + '/temp/*.xml')[0]
    filename_parts = new_file.split('/')[-1].split('.')[:-1]
    new_name = destination_folder + '/data/{man}/{fols}/{man}.{fols}.{ed}.xml'.format(man=filename_parts[0], fols=filename_parts[1], ed=filename_parts[2])
    fol_add = 2
    new_urn = ''
    while os.path.isfile(new_name):
        new_name = destination_folder + '/data/{man}/{fols}{add}/{man}.{fols}{add}.{ed}.xml'.format(man=filename_parts[0], fols=filename_parts[1], ed=filename_parts[2], add=fol_add)
        fol_add += 1
        new_urn = 'urn:cts:formulae:{}.{}{}.{}'.format(filename_parts[0], filename_parts[1], fol_add, filename_parts[2])
    new_folder = os.path.dirname(new_name)
    makedirs(new_folder, exist_ok=True)
    rename(new_file, new_name)
    # Need to change the URN if it matches a previously written URN
    if new_urn:
        xml = etree.parse(new_name)
        for edition_div in xml.xpath('/tei:TEI/tei:text/tei:body/tei:div[@type="edition"]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
            edition_div.set('n', new_urn)
        xml.write(new_name, encoding='utf-8', pretty_print=True)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(new_name), metadata_transformation_xslt, '-o:{folder}/__capitains__.xml'.format(folder=new_folder)])
    md_xml = etree.parse('{folder}/__capitains__.xml'.format(folder=new_folder))
    for is_version_of in md_xml.xpath('//dct:isVersionOf', namespaces={'dct': 'http://purl.org/dc/terms/'}):
        is_version_of.text = 'urn:cts:formulae:{}.{}'.format(corpus_name, form_num)
    md_xml.write('{folder}/__capitains__.xml'.format(folder=new_folder), encoding='utf-8', pretty_print=True)
    makedirs('{base_folder}/data/{corpus}/{entry}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num), exist_ok=True)
    temp_file = '{base_folder}/data/{corpus}/{entry}/{man_filename}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num, man_filename='.'.join(filename_parts) + '.xml')
    temp_files.append(temp_file)
    with open(temp_file, mode="w") as f:
        f.write('<xml/>')
    remove_space_before_note(new_name)

for latin in latins:
    print(latin)
    remove_tei_dtd_reference(latin)
    form_num = produce_form_num(latin)
    new_name = '{base_folder}/data/{corpus}/{entry}/{corpus}.{entry}.lat001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(latin), text_transformation_xslt])
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(new_name), metadata_transformation_xslt, '-o:{base_folder}/data/{corpus}/{entry}/__capitains__.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)])
    remove_space_before_note(new_name)
    
# Delete the temporary files
for temp_file in temp_files:
    remove(temp_file)

# Create collection-level capitains create_capitains_files
sub_folders = glob(destination_folder + '/data/*')
for sub_folder in sub_folders:
    meta_filename = sub_folder + '/temp.xml'
    new_meta_filename = sub_folder + '/__capitains__.xml'
    if not os.path.isfile(meta_filename):
        with open(meta_filename, mode="w") as f:
            f.write('<xml/>')
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(meta_filename), collection_metadata_xslt, '-o:{}'.format(meta_filename)])
    rename(meta_filename, new_meta_filename)
