from glob import glob
import re
from os import makedirs, environ, getcwd, remove, rename
import os.path
from lxml import etree
from collections import defaultdict
import logging
import argparse
from tqdm import tqdm
from util import subprocess_run, get_logger
from bs4 import BeautifulSoup
from transform_cte_to_dll_checks import check_if_notes_exist, check_paths_in_capitains, check_transcriptions_got_proper_names, check_if_collection_exists

home_dir = environ.get('HOME', '')

parser=argparse.ArgumentParser(description="Script to transform CTE-XML files to ???")
default_saxon_location = home_dir + '/Downloads/SaxonHE10-1J/saxon-he-10.1.jar'
parser.add_argument("saxon_location", type=str,default=default_saxon_location)
parser.add_argument("corpus_name", type=str,default='andecavensis')
parser.add_argument("formulae_collections_md_file", type=str,default='/home/matt/formulae-corpora/data/formulae_collection/__capitains__.xml')
default_scripts_folder = home_dir + '/scripts'
parser.add_argument("scripts_folder", type=str, default=default_scripts_folder, 
                    help='Path to your local copy of https://github.com/Formulae-Litterae-Chartae/scripts')
parser.add_argument("--log_file", type=str, default='/home/thorben.schomacker/git/scripts/results/transform_cte_to_dll.log',
                    help='If set to a valid path: Path where the log is written to. Otherwise it will be the console.')
args=parser.parse_args()



logger = get_logger()
# TODO: set the level via cl argument
logger.setLevel('WARNING')
log_file_path=args.log_file.lower()
# create the log_file
with open(log_file_path, 'w'): pass
fh = logging.FileHandler(log_file_path)
fh.setLevel('WARNING')
logger.addHandler(fh)

tqdm_switch = logger.getEffectiveLevel() > 30
saxon_location = args.saxon_location

scripts_folder = args.scripts_folder


text_transformation_xslt = scripts_folder + '/corpus_transformation_scripts/Formulae/transform_cte_to_dll.xsl'
metadata_transformation_xslt = scripts_folder + '/corpus_transformation_scripts/Formulae/create_capitains_files.xsl'
collection_metadata_xslt = scripts_folder + '/corpus_transformation_scripts/Formulae/create_collection_capitains_files.xsl'
corpus_name = args.corpus_name # Used to build the folder structure
logging.debug('corpus_name: '+corpus_name)
destination_folder = getcwd() # The base folder where the corpus folder structure should be built
latins = glob(destination_folder + '/Latin/*.xml')
germans = glob(destination_folder + '/Deutsch/*.xml')
transcriptions = glob(destination_folder + '/Transkripte/*.xml', recursive=True)
temp_files = []
ns = {'dct': "http://purl.org/dc/terms/", 'dc': "http://purl.org/dc/elements/1.1/", 'cpt': "http://purl.org/capitains/ns/1.0#", 'tei': 'http://www.tei-c.org/ns/1.0'}

formulae_collections_md_file = args.formulae_collections_md_file
if not os.path.isfile(formulae_collections_md_file): raise FileNotFoundError(formulae_collections_md_file)
logger.info('Parse: {}'.format(formulae_collections_md_file))
form_coll_md = etree.parse(formulae_collections_md_file)
mss_edition_dict = defaultdict(set)
title_id_dict = dict()
for f_c in form_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
    form_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(formulae_collections_md_file), f_c.get('path')))
    form_corp_md = etree.parse(form_corp_md_path)
    for f_corp in form_corp_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
        form_md_path = os.path.normpath(os.path.join(os.path.dirname(form_corp_md_path), f_corp.get('path')))
        form_md = etree.parse(form_md_path)
        for c in form_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
            for t in c.xpath('./dc:type/text()', namespaces=ns):
                if t  == 'cts:edition':
                    title_id_dict[c.xpath('./cpt:identifier/text()', namespaces=ns)[0]] = c.xpath('./dc:title/text()', namespaces=ns)[0].replace(' (lat)', '')
        for c in form_md.xpath('/cpt:collection/cpt:members/cpt:collection[@identifier]', namespaces=ns):
            mss_path = os.path.normpath(os.path.join(os.path.dirname(form_md_path), c.get('path')))
            if not os.path.isfile(mss_path):
                raise FileNotFoundError(mss_path)
            mss_md = etree.parse(mss_path)
            for mss in mss_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
                if mss.xpath('dc:type', namespaces=ns)[0].text == 'transcription':
                    mss_edition_dict[mss.xpath('cpt:identifier', namespaces=ns)[0].text].add(form_md.xpath('/cpt:collection/cpt:identifier', namespaces=ns)[0].text)

# sanity checks
if not (len(transcriptions)  >= len(latins)):
    logger.warning("The number of transcriptions ({}) should always be greater or equal to the number of latins ({})".format(len(transcriptions), len(latins)))

if not ( len(germans) == len(latins) ):
    logger.warning("The number of germans ({}) should always be equal to the number of latins ({})".format(len(germans), len(latins)))

def check_xml_file_name(file_name:str, logger:logging.Logger, is_transcription=False) -> bool:
    """
    Checks wether the given file_name matches the patterns later required in the transformation process.
    Although the regex could be optimized in terms of execution time - readability of the code should be kept in mind.
    """
    file_name=file_name.split('/')[-1]
    # collection specific matching
    ## Angers
    if re.match(r"Angers [1-9][0-9]?( Deutsch)?.xml", file_name): return True 
    if re.match(r"Angers 0 Titel( Deutsch)?.xml", file_name): return True 
    if re.match(r"Angers Einschub Weltzeitalter, Schalttagsberechnung und computus( Deutsch)?.xml", file_name): return True 
    ## Auvergne
    if re.match(r"Auvergne [1-6]( Deutsch)?.xml", file_name): return True 
    ## Bourges
    if re.match(r"Bourges [A-C] [1-9][0-9]?( [a-m])?( Deutsch)?.xml", file_name): return True 
    ## Marculf
    if re.match(r"Marculf (I{1,2}|0),?[0-9]*[a-f]? ?(Capitulatio|Praefatio)?( Deutsch)?\.xml", file_name): return True 
    if re.match(r"Marculf Ergänzung [1-9],[1-9]?( Deutsch)?.xml", file_name): return True 
    ## Tours
    if re.match(r"Tours( Ergänzung)? [0-9][0-9]?[a-b]?(\(A\)|\(B\))?( Capitulatio)?( Deutsch)?.xml", file_name): return True 

    # German matching
    if re.match(r"[a-zA-Z]+ [A-Z]*[0-9 ]+[ ]*Deutsch.xml", file_name):
        return True
    if re.match(r"[a-zA-Z]+ [A-Z]*[0-9 ]+Incipit+[ ]+Deutsch.xml", file_name):
        return True
    if re.match(r"Sens Ergänzung Deutsch.xml", file_name):
        return True
    # Latin matching
    if re.match(r"[a-zA-Z]+ [A-Z]*[0-9 ]+Incipit.xml", file_name):
        return True
    if re.match(r"Sens [A-Z]*[0-9 ]+[ ]*.xml", file_name):
        return True
    if re.match(r"Sens Ergänzung.xml", file_name):
        return True
    # Transcription matching
    if '(' in file_name or ')' in file_name:
        if is_transcription:
            if re.match(r".*\(.*\).xml", file_name):
                return True
            else:
                ValueError("{} does not met the file naming conventions for transcriptions. Leaving it unchanged will cause errors later.".format(file_name))
        else:
            ValueError("{} does not met the file naming conventions. Only transcriptions should contain '(' and ')'".format(file_name))
    # Fallback case, when none of the previous patterns matched
    raise ValueError("{} does not met the file naming conventions. Leaving this name unchanged will cause errors later.".format(file_name))
    
for file_name in germans+latins:
    try:
        check_xml_file_name(file_name, logger)
    except ValueError as e:
        logger.error('{}'.format(e))
for file_name in transcriptions:
    try:
        check_xml_file_name(file_name, logger, is_transcription=True)
    except ValueError as e:
        logger.error('{}'.format(e))

def remove_space_before_note(filename):
    #logger.info(filename+' exists: '+str(os.path.isfile(filename)))
    try:
        with open(filename) as f:
            text = f.read()
    except FileNotFoundError as e:
        # try: 
        #     from pathlib import Path
        #     file_path = Path(filename)
        #     try:
        #         file_path.touch(exist_ok=True)
        #         logger.info('file {} created'.format(filename))
        #     except IsADirectoryError as e: 
        #         filename.mkdir(parents=True, exist_ok=True)
        #         logger.info('directory {} created'.format(filename))
        #     with open(filename) as f:
        #         text = f.read()
        # except FileNotFoundError as e:
        logger.error('Failed to open {} with this error: {}'.format(filename, repr(e)))
        logger.error('This file should have been created with one the subprocess.run commands. This indicates an error with the jar file.' )
        raise e
    text = re.sub(r'\s+<note', '<note', text)
    text = re.sub(r'<seg type="italic;"><w>([^<]+)</w></seg>', r'<w><seg type="italic;">\1</seg></w>', text)
    text = re.sub(r'</w><w>', '', text)
    #patt_1 = re.compile(r'</w><seg type="italic;"><w>([^<]+)</w></seg>')
    #patt_2 = re.compile(r'(<seg type="italic;">[^<]+</seg>)</w><w>([^<]+</w>)')
    #while re.search(patt_1, text) or re.search(patt_2, text):
        #text = re.sub(patt_1, r'<seg type="italic;">\1</seg></w>', text)
        #text = re.sub(patt_2, r'\1\2', text)

    # @TODO: add a line that replace seg with anchor. Needs to be checked
    with open(filename, mode="w") as f:
        #logger.info("write: "+filename)
        f.write(text)
    # Add urn and title to title_id_dict
    xml = etree.parse(filename)
    try:
        urn = xml.xpath('/tei:TEI/tei:text/tei:body/tei:div/@n', namespaces=ns)[0].replace('deu001', 'lat001')
    except IndexError as ie:
        logger.error("There was an error, when processing {}".format(filename))
        raise ie
    title = xml.xpath('/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title', namespaces=ns)[0].text
    title_id_dict[urn] = title
        
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
        
def produce_form_num(filename:str) -> str:
    """
    Extract the number of the form by a pattern matching process
    """
    if 'Weltzeitalter' in filename:
        form_num = 'computus'
    elif 'Capitula' in filename:
        form_num = '0_capitula'
        if 'II' in filename:
            form_num = '2_capitula'
        elif 'I' in filename:
            form_num = '1_capitula'
        elif ' P3' in filename:
            form_num = '2_capitula'
        elif ' Ko2' in filename:
            form_num = '3_capitula'
    elif 'Sens' in filename:
        if 'Incipit' in filename:
            form_num = 'form_a_000'
        elif 'Ergänzung' in filename:
            form_num = 'form_b_ergaenzung'
        else:
            sens_parts = re.search(r'Sens ([A-C]) (\d+) ?([a-m])?', filename)
            form_num = 'form_{}_{:03}{}'.format(sens_parts[1].lower(), int(sens_parts[2]), sens_parts[3] if sens_parts[3] else '')
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
            form_num = 'form2_' + '{:03}'.format(int(re.sub(r'.*?(\d+)(\w?).*', r'\1', filename)))
            if re.sub(r'.*?(\d+)(\w?).*', r'\2', filename):
                form_num += '_' + re.sub(r'.*?(\d+)(\w?).*', r'\2', filename)
    elif 'Tours 40' in filename:
        form_num = 'form040_' + re.sub(r'.*Tours 40\((.)\).*', r'\1', filename).lower()
    elif 'Bourges' in filename:
        bourges_parts = re.search(r'Bourges ([A-C]) (\d+) ?([a-m])?', filename)
        form_num = 'form_{}_{:03}{}'.format(bourges_parts[1].lower(), int(bourges_parts[2]), bourges_parts[3] if bourges_parts[3] else '')
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
    
    logging.debug('Generated {} as form_num of {}'.format(form_num,filename))
    return form_num


logger.info("Start with German(s)")

def process_german(german:str, corpus_name:str, logger:logging.Logger) -> None:
    logger.debug("Processing: "+german)
    remove_tei_dtd_reference(german)
    form_num = produce_form_num(german)
    if corpus_name=='angers':
        corpus_name='andecavensis'
    new_name = '{base_folder}/data/{corpus}/{form}/{corpus}.{form}.deu001.xml'.format(base_folder=destination_folder, corpus=corpus_name, form=form_num)
    # This subprocess creates the location for the files. 
    subprocess_run(['java', '-jar',  saxon_location, '-s:{}'.format(german), text_transformation_xslt],logging)
    remove_space_before_note(new_name)


for german in tqdm(germans, desc="Process German translation(s)", disable=(logger.getEffectiveLevel() > 30)):
    process_german(german, corpus_name, logger)


from transform_cte_to_dll_checks import check_input_regesten_format
from transform_cte_to_dll_checks import check_fols
# Since all following steps rely on the existance and format of the regesten file. It should be checked!
check_input_regesten_format(destination_folder, logger)
logger.setLevel('WARNING')
if 0==len(transcriptions):logger.warning("No transcriptions found!")
logger.info("Start with transcription(s)")
collections_not_found = set()
collections_found = set()
for transcription in tqdm(sorted(transcriptions), desc="Process transcription(s)"):
    
    if not corpus_name in os.path.split(transcription)[-1].lower(): 
        if corpus_name == 'marculf' and 'markulf' in os.path.split(transcription)[-1].lower(): 
            pass
        elif corpus_name == 'andecavensis' and 'angers' in os.path.split(transcription)[-1].lower(): 
            pass
        else:
            raise ValueError("The file name of {} does not include the corpus name {}. This will cause errors later.".format(transcription, corpus_name))

    logging.debug("process transcription: "+transcription)
    remove_tei_dtd_reference(transcription)
    form_num = produce_form_num(transcription)
    try:
        manuscript = re.search(r'\((\w+)\)\Z', transcription.replace('.xml', '')).group(1).lower()
    except:
        print(transcription)
        raise AttributeError
    logging.debug('manuscript: '+manuscript)
    transcript_folders = glob('{base_folder}/data/{manuscript}/*'.format(base_folder=destination_folder, manuscript=manuscript))
    
    subprocess_run(['java', '-jar',  saxon_location, '{}'.format(transcription), text_transformation_xslt], logger)
    allocated_temp_files= glob(destination_folder + '/temp/*.xml')
    if len(allocated_temp_files) > 0: 
        logging.debug('Allocated new files: {} at {}'.format(allocated_temp_files, destination_folder + '/temp/*.xml'))
    else:
        logger.error('There are no file {} at {}. This will immediately cause an error. This resulted from the previous not been done properly.'.format(allocated_temp_files, destination_folder + '/temp/*.xml'))
    
    new_file = allocated_temp_files[0]
    filename_parts = new_file.split('/')[-1].split('.')[:-1]
    #filename_parts[1] = filename_parts[1].replace(" ", "")
    logging.debug("filename_parts {}".format(filename_parts))
    man = filename_parts[0]
    
    if man != manuscript: 
        logger.warning("manuscript ({}) and man ({}) differ, but should be the same !".format(man, manuscript))
        if man == corpus_name:
            logging.warning("corpus_name and man have the same value: {} . They should differ!".format(man))
    
    if check_if_collection_exists(man, "transcription"):
        collections_found.add(man)
    else:
        collections_not_found.add(man)
        #man = manuscript
        #logging.debug("Assigned as: {} the value for man based on manuscript".format(man))
    
    
    check_fols(filename_parts[0], filename_parts[1], logger)
    new_name = destination_folder + '/data/{man}/{fols}/{man}.{fols}.{ed}.xml'.format(man=man, fols=filename_parts[1], ed=filename_parts[2])
    fol_add = 1
    new_urn = ''
    while os.path.isfile(new_name):
        fol_add += 1
        new_name = destination_folder + '/data/{man}/{fols}{add}/{man}.{fols}{add}.{ed}.xml'.format(man=man, fols=filename_parts[1], ed=filename_parts[2], add=fol_add)
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
        logger.debug('Changed urn to {} in {} using the regest file.'.format(new_urn, new_name))
    else:
        # Am I not sure, whether this is an error or expected behavior
        logger.debug('No urn detected for {}.'.format(new_name))

    logger.debug('Create the capitains file for {} in {} using the regest file.'.format(new_name,new_folder))
    subprocess_run(['java', '-jar',  saxon_location, '{}'.format(new_name), 
                    metadata_transformation_xslt, '-o:{folder}/__capitains__.xml'.format(folder=new_folder)],logging)
    capitains_file_path = os.path.join(new_folder, '__capitains__.xml')
    if not os.path.isfile(capitains_file_path): raise FileNotFoundError(capitains_file_path)
    logger.info(capitains_file_path)
    md_xml = etree.parse(capitains_file_path)
    for is_version_of in md_xml.xpath('//dct:isVersionOf', namespaces={'dct': 'http://purl.org/dc/terms/'}):
        is_version_of.text = 'urn:cts:formulae:{}.{}'.format(corpus_name, form_num)
    mss_urn = 'urn:cts:formulae:{}.{}.{}'.format(filename_parts[0], filename_parts[1], filename_parts[2])
    if new_urn:
        mss_urn = new_urn
        filename_parts[1] = filename_parts[1] + str(fol_add)
    
    id_of_corresponding_document = 'urn:cts:formulae:{}.{}'.format(corpus_name, form_num)

    mss_edition_dict[mss_urn].add(id_of_corresponding_document)
    logging.debug("Transcription: "+mss_urn+" mapped to this document:"+ id_of_corresponding_document)
    for s_md in md_xml.xpath('//cpt:structured-metadata', namespaces=ns):
        for mss_edition in mss_edition_dict[mss_urn]:
            new_element = etree.Element('{http://purl.org/dc/terms/}isVersionOf', nsmap=ns)
            new_element.text = mss_edition
            s_md.append(new_element)
    from mss_edition_csv_to_xml import make_temp_id
    #logger.info('mss_edition_dict:'+str(mss_edition_dict))
    
    
    #form_id_list =  [make_temp_id(mss_urn)]
    for title_id in title_id_dict.keys():
        if corpus_name in title_id and form_num in title_id:
            logging.debug('Matching entry found: '+title_id)

    form_id_list = mss_edition_dict[mss_urn]
    title_value =  md_xml.xpath('/cpt:collection/dc:title', namespaces=ns)[0].text + ': ' + '/'.join([title_id_dict[form_id + '.lat001'] for form_id in form_id_list])
    logger.info('title_value: '+title_value)
    md_xml.xpath('/cpt:collection/dc:title', namespaces=ns)[0].text = title_value 

    md_xml.write('{folder}/__capitains__.xml'.format(folder=new_folder), encoding='utf-8', pretty_print=True)
    makedirs('{base_folder}/data/{corpus}/{entry}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num), exist_ok=True)
    temp_file = '{base_folder}/data/{corpus}/{entry}/{man_filename}'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num, man_filename='.'.join(filename_parts) + '.xml')
    temp_files.append(temp_file)
    # Thorben (01.04.25): Why do we need these empty temp files?
    with open(temp_file, mode="w") as f:
        logging.debug("write: "+temp_file)
        f.write('<!--I am a temp file, that should have been deleted.-->\n')
        f.write('<xml/>')
    remove_space_before_note(new_name)
    try:
        check_transcriptions_got_proper_names(manuscript, new_name, logger)
    except Exception as e:
        logger.error(str(e))

if collections_not_found: 
    logger.error("{} collections not found: {}".format(len(collections_not_found), collections_not_found))
else:
    logger.info("All collections found! {}".format(collections_found))


from hss_editionen_tool import check_hss_editionen
from transform_cte_to_dll_checks import check_hss_editionen_file
try:
    check_hss_editionen_file(hss_editionen_file_path='~/git/scripts/formel_transform/output/sens/hss_editionen.xml', logger=logger) 
except Exception as e:
    logger.error(e)

logger.setLevel('WARNING')
if 0==len(latins):logger.warning("No Latin documents found!")
logger.info("Start with latin(s)")
#check_hss_editionen()
for latin in tqdm(latins, desc="Process latin(s)", disable=tqdm_switch, leave=not tqdm_switch):
    if 'Ergänzung' in latin: print('Process:'+latin)
    remove_tei_dtd_reference(latin)
    form_num = produce_form_num(latin)
    new_name = '{base_folder}/data/{corpus}/{entry}/{corpus}.{entry}.lat001.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    # does latin exist?
    logging.debug('Process: {}'.format(latin))
    new_name_existed_before_transforming = os.path.isfile(new_name)
    subprocess_run(['java', '-jar',  saxon_location, '-s:{}'.format(latin), text_transformation_xslt],logger)
    if not new_name_existed_before_transforming and os.path.isfile(new_name): logger.info('{} was created.'.format(new_name))
    if not os.path.isfile(new_name): logger.error('{} does not exist. It have been created previously.'.format(new_name))
    if 'Ergänzung' in latin: print('new_name:'+new_name)
    
    capitains_file_output_path = '{base_folder}/data/{corpus}/{entry}/__capitains__.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)
    logger.info('Create '+capitains_file_output_path)
    
    subprocess_run(['java', '-jar',  saxon_location, '-s:{}'.format(new_name), metadata_transformation_xslt, 
                                        '-o:{base_folder}/data/{corpus}/{entry}/__capitains__.xml'.format(base_folder=destination_folder, corpus=corpus_name, entry=form_num)], logger)
    # if True:
    #     print(new_name)
    #     tree = ET.parse(new_name)
    #     root = tree.getroot()
    #     all_checks_passed = True
    #     for collection in root.findall('.//{*}collection'):
        
    remove_space_before_note(new_name)
    check_if_notes_exist(input_file='{}'.format(latin),transformed_file='{}'.format(new_name), logger=logger)
    try:
        check_paths_in_capitains(capitains_file_output_path,logger)
    except Exception as e:
        logger.error(str(e))
# Delete the temporary files
keep_temp_files_for_debugging = False
if (not keep_temp_files_for_debugging) or logger.getEffectiveLevel() > 19:
    for temp_file in temp_files:
        remove(temp_file)
    logger.debug("{} temp_files have been removed".format(len(temp_files)))
else:
    logger.debug("Temp files kept for debugging purposes. "
                 "They have to be removed eventually, at least before copying the files to the corpora directory.")

# Create collection-level capitains create_capitains_files
from util import check_capitains_rng
check_capitains_rng()

sub_folders = glob(destination_folder + '/data/*')
for sub_folder in sub_folders:
    meta_filename = sub_folder + '/temp.xml'
    new_meta_filename = sub_folder + '/__capitains__.xml'
    if not os.path.isfile(meta_filename):
        with open(meta_filename, mode="w") as f:
            logging.debug("meta_filename: "+meta_filename)
            f.write('<xml/>')
    subprocess_run(['java', '-jar',  saxon_location, '{}'.format(meta_filename), collection_metadata_xslt, '-o:{}'.format(meta_filename)],logger=logger)
    rename(src=meta_filename,  dst=new_meta_filename)

### Finish up with a sanity check

from transform_cte_to_dll_checks import check_file_creation, check_output_regesten_existance
if check_file_creation(corpus_name, latins, germans, transcriptions, logger) and check_output_regesten_existance(corpus_folder='{base_folder}/data/{corpus}'.format(base_folder=destination_folder, corpus=corpus_name), logger=logger):
    logger.info("Success! No errors detected in the file creation process.")