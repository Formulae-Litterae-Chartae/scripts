from glob import glob
import re
import subprocess
from os import makedirs

latins = [x for x in glob('/home/matt/Documents/Angers_XML/*.xml') if 'Deutsch' not in x]
germans = [x for x in glob('/home/matt/Documents/Angers_XML/*.xml') if 'Deutsch' in x]
transcriptions = glob('/home/matt/Documents/Angers_XML/Transkripte/*Fu2*.xml')

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
    form_num = "{:03}".format(int(german.replace('.xml', '').split(' ')[1]))
    new_name = '/home/matt/results/formulae/data/andecavensis/form{entry}/andecavensis.form{entry}.deu001.xml'.format(entry=form_num)
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(german), '/home/matt/docx_tei_cte_conversion/transform_cte_to_dll.xsl', '-o:{}'.format(new_name)])
    remove_space_before_note(new_name)
    
for transcription in transcriptions:
    remove_tei_dtd_reference(transcription)
    form_num = "{:03}".format(int(transcription.replace('.xml', '').split(' ')[1]))
    manuscript = transcription.split('(')[1].split(')')[0].lower()
    new_name = '/home/matt/results/formulae/data/andecavensis/form{entry}/andecavensis.form{entry}.{manuscript}.xml'.format(entry=form_num, manuscript=manuscript)
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(transcription), '/home/matt/docx_tei_cte_conversion/transform_cte_to_dll.xsl', '-o:{}'.format(new_name)])
    remove_space_before_note(new_name)

for latin in latins:
    remove_tei_dtd_reference(latin)
    form_num = "{:03}".format(int(latin.replace('.xml', '').split(' ')[1]))
    new_name = '/home/matt/results/formulae/data/andecavensis/form{entry}/andecavensis.form{entry}.lat001.xml'.format(entry=form_num)
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(latin), '/home/matt/docx_tei_cte_conversion/transform_cte_to_dll.xsl', '-o:{}'.format(new_name)])
    subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(new_name), '/home/matt/docx_tei_cte_conversion/create_cts_files_new.xsl', '-o:/home/matt/results/formulae/data/andecavensis/form{entry}/__cts__.xml'.format(entry=form_num)])
    remove_space_before_note(new_name)
