from glob import glob
import re
import subprocess
from os import makedirs, environ, getcwd, remove, rename
import os.path

home_dir = environ.get('HOME', '')
saxon_location = home_dir + '/Downloads/SaxonHE9-8-0-11J/saxon9he.jar'
text_transformation_xslt = home_dir + '/docx_tei_cte_conversion/corpus_transformation_scripts/Formulae/transform_cte_to_dll.xsl'
metadata_transformation_xslt = home_dir + '/docx_tei_cte_conversion/corpus_transformation_scripts/Formulae/create_capitains_files.xsl'
collection_metadata_xslt = home_dir + '/docx_tei_cte_conversion/corpus_transformation_scripts/Formulae/create_collection_capitains_files.xsl'
corpus_name = 'andecavensis' # Used to build the folder structure
destination_folder = getcwd() # The base folder where the corpus folder structure should be built
latins = glob(destination_folder + '/Latin/*.xml')
germans = glob(destination_folder + '/Deutsch/*.xml')
transcriptions = [] #glob(destination_folder + '/Transkripte/*.xml')
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
    text = text.replace('<!DOCTYPE TEI PUBLIC "-//TEI//DTD TEI P5//EN" "tei.dtd" >', '')
    with open(filename, mode="w") as f:
        f.write(text)

for german in germans:
    remove_tei_dtd_reference(german)
    if 'Weltzeitalter' in german:
        new_name = '{base_folder}/data/{corpus}/computus/{corpus}.computus.deu001.xml'.format(base_folder=destination_folder, corpus=corpus_name)
    else:
        form_num = "{:03}".format(int(german.replace('.xml', '').split(' ')[1].split(',')[-1]))
        new_name = '{base_folder}/data/{corpus}/form{entry}/{corpus}.form{entry}.deu001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(german), text_transformation_xslt])
    remove_space_before_note(new_name)
    
for transcription in sorted(transcriptions):
    remove_tei_dtd_reference(transcription)
    if 'Weltzeitalter' in transcription:
        form_num = 'computus'
    else:
        form_num = 'form' + "{:03}".format(int(transcription.replace('.xml', '').split(' ')[1].split(',')[-1]))
    manuscript = re.search(r'\((\w+)\)\Z', transcription.replace('.xml', '')).group(1).lower()
    transcript_folders = glob('{base_folder}/data/{manuscript}/*'.format(base_folder=destination_folder, manuscript=manuscript))
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(transcription), text_transformation_xslt])
    new_file = glob(destination_folder + '/temp/*.xml')[0]
    filename_parts = new_file.split('/')[-1].split('.')[:-1]
    new_name = destination_folder + '/data/{man}/{fols}/{man}.{fols}.{ed}.xml'.format(man=filename_parts[0], fols=filename_parts[1], ed=filename_parts[2])
    fol_add = 2
    while os.path.isfile(new_name):
        new_name = destination_folder + '/data/{man}/{fols}{add}/{man}.{fols}{add}.{ed}.xml'.format(man=filename_parts[0], fols=filename_parts[1], ed=filename_parts[2], add=fol_add)
        fol_add += 1
    new_folder = os.path.dirname(new_name)
    makedirs(new_folder, exist_ok=True)
    rename(new_file, new_name)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(new_name), metadata_transformation_xslt, '-o:{folder}/__capitains__.xml'.format(folder=new_folder)])
    makedirs('{base_folder}/data/{corpus}/{entry}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num), exist_ok=True)
    temp_file = '{base_folder}/data/{corpus}/{entry}/{man_filename}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num, man_filename='.'.join(filename_parts) + '.xml')
    temp_files.append(temp_file)
    with open(temp_file, mode="w") as f:
        f.write('<xml/>')
    remove_space_before_note(new_name)

for latin in latins:
    remove_tei_dtd_reference(latin)
    if 'Weltzeitalter' in latin:
        form_num = "computus"
    else:
        form_num = 'form' + "{:03}".format(int(latin.replace('.xml', '').split(' ')[1].split(',')[-1]))
    new_name = '{base_folder}/data/{corpus}/{entry}/{corpus}.{entry}.lat001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    subprocess.run(['java', '-jar',  saxon_location, '{}'.format(latin), text_transformation_xslt])
    # subprocess.run(['java', '-jar',  saxon_location, '{}'.format(new_name), metadata_transformation_xslt, '-o:{base_folder}/data/{corpus}/{entry}/__capitains__.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)])
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
