from glob import glob
import re
import subprocess
from os import makedirs, environ

home_dir = environ.get('HOME', '')
saxon_location = home_dir + '/Downloads/SaxonHE9-8-0-11J/saxon9he.jar'
text_transformation_xslt = home_dir + '/docx_tei_cte_conversion/corpus_transformation_scripts/Formulae/transform_cte_to_dll.xsl'
metadata_transformation_xslt = home_dir + '/docx_tei_cte_conversion/corpus_transformation_scripts/Formulae/create_cts_files_new.xsl'
corpus_name = 'andecavensis' # Used to build the folder structure
destination_folder = home_dir + '/Documents/Angers_XML' # The base folder where the corpus folder structure should be built
latins = glob(home_dir + '/Documents/Angers_XML/Latin/*.xml')
germans = glob(home_dir + '/Documents/Angers_XML/Deutsch/*.xml')
transcriptions = glob(home_dir + '/Documents/Angers_XML/Transkripte/*.xml')

def remove_space_before_note(filename):
    with open(filename) as f:
        text = f.read()
    text = re.sub(r'\s+<note', '<note', text)
    with open(filename, mode="w") as f:
        f.write(text)
        
def remove_tei_dtd_reference(filename):
    with open(filename) as f:
        text = f.read()
    text = text.replace('<!DOCTYPE TEI PUBLIC "-//TEI//DTD TEI P5//EN" "tei.dtd" >', '')
    with open(filename, mode="w") as f:
        f.write(text)

for german in germans:
    remove_tei_dtd_reference(german)
    form_num = "{:03}".format(int(german.replace('.xml', '').split(' ')[1].split(',')[-1]))
    new_name = '{base_folder}/data/{corpus}/form{entry}/{corpus}.form{entry}.deu001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(german), text_transformation_xslt, '-o:{}'.format(new_name)])
    remove_space_before_note(new_name)
    
for transcription in transcriptions:
    remove_tei_dtd_reference(transcription)
    form_num = "{:03}".format(int(transcription.replace('.xml', '').split(' ')[1].split(',')[-1]))
    manuscript = re.search(r'\((\w+)\)\Z', transcription.replace('.xml', '')).group(1).lower()
    new_name = '{base_folder}/data/{corpus}/form{entry}/{corpus}.form{entry}.{manuscript}.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num, manuscript=manuscript)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(transcription), text_transformation_xslt, '-o:{}'.format(new_name)])
    remove_space_before_note(new_name)

for latin in latins:
    remove_tei_dtd_reference(latin)
    form_num = "{:03}".format(int(latin.replace('.xml', '').split(' ')[1].split(',')[-1]))
    new_name = '{base_folder}/data/{corpus}/form{entry}/{corpus}.form{entry}.lat001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(latin), text_transformation_xslt, '-o:{}'.format(new_name)])
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(new_name), metadata_transformation_xslt, '-o:{base_folder}/data/{corpus}/form{entry}/__cts__.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)])
    remove_space_before_note(new_name)
