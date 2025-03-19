from glob import glob
from bs4 import BeautifulSoup
import os
import re 
import logging

# This file holds all checks for the cte to dll transformation process
# In theory these could be the basis for unit tests. 
# But I wanted to execute them directly in the tranformation script.
# Using them for both practices could be desirable in the future. 


def check_file_creation(corpus_name:str, latins:list[str], germans:list[str], transcriptions:list[str],logger:logging.Logger, base_folder:str=".") -> bool:
    """
    sanity check for the transcription files. To ensure proper processing in later steps.
    """
    german_latin_path = os.path.join(base_folder,'data',corpus_name)
    german_latin_path_subfolders = [ f.path for f in os.scandir(german_latin_path) if f.is_dir() ]
    check_passed = True
    if len(german_latin_path_subfolders) != len(latins):
        logger.error("Check FAILed! {} has {} folders. But it should have {} folders one for each Latin files.".format(german_latin_path, len(german_latin_path_subfolders), len(latins)))
        check_passed = False
    else: 
        logger.info("Check passed! Identified {} has {} folders, one for each Latin file.".format(german_latin_path, len(german_latin_path)))
    if len(german_latin_path_subfolders) != len(germans):
        logger.error("Check FAILed! {} has {} folders. But it should have {} folders one for each German files.".format(german_latin_path, len(german_latin_path_subfolders), len(germans)))
        check_passed = False
    else: 
        logger.info("Check passed! Identified {} has {} folders, one for each German file.".format(german_latin_path, len(german_latin_path)))
    possible_trancriptions_folders = glob(base_folder + '/data/*')
    transcription_subfolders = []
    for transcription_folder in possible_trancriptions_folders:
        # exclude the folder with the German and Latin files
        if os.path.split(transcription_folder)[-1] != corpus_name:
            transcription_subfolders = transcription_subfolders + [ f.path for f in os.scandir(transcription_folder) if f.is_dir() ]
    if len(transcription_subfolders) == len(transcriptions):
        logger.info("Check passed! Identified {} as possible transcription folder(s). It has {} folders, one for each transcription.".format(possible_trancriptions_folders, len(transcription_subfolders), len(transcriptions)))
    else:
        logger.error("Check FAILed! Identified {} as possible transcription folder(s). It has {} folders, but should have {} folders one for each transcription.".format(possible_trancriptions_folders, len(transcription_subfolders), len(transcriptions)))
    german_latin_path = os.path.join(base_folder,'data',corpus_name)
    german_latin_path_subfolders = [ f.path for f in os.scandir(german_latin_path) if f.is_dir() ]
    if not check_passed:
        raise Exception("Something went wrong during the file creation process. Please check the previous error logs.")
    else:
        return check_passed
    

def check_if_notes_exist(input_file, transformed_file,logger):
    """
    sanity check to see whether all notes from the input file found their way into the transformed_file
    """
    from bs4 import BeautifulSoup
    with open(input_file, 'r') as f:
        file = f.read() 
        soup = BeautifulSoup(file, 'xml')
        input_apparatus_notes = soup.find_all("note", type="a1")
        input_apparatus_notes_unique_target_ends = set([ note['targetEnd'] for note in input_apparatus_notes ])
    
    with open(transformed_file, 'r') as f:
        file = f.read() 
        soup = BeautifulSoup(file, 'xml')
        transformed_apparatus_notes = soup.find_all("note", type="a1")
        transformed_apparatus_notes_unique_target_ends = set([note['targetEnd'] for note in transformed_apparatus_notes ])

    if not input_apparatus_notes_unique_target_ends == transformed_apparatus_notes_unique_target_ends:
        logger.error('Not all notes where transformed from {} ({}) to {} ({})'.format(input_file, 
                                                                                        input_apparatus_notes_unique_target_ends,
                                                                                        transformed_file,
                                                                                        transformed_apparatus_notes_unique_target_ends))



def check_input_regesten_format(destination_folder,logger):
    """
    checks whether the regest have the proper format to be further processed 
    as a form of sanity check
    """

    docid_pattern_without_prefixes = re.compile("[0-9][0-9][0-9]") #e.g., <regest docId="001">
    formel_number_pattern = re.compile("form[0-9][0-9][0-9]")
    formel_number_pattern_with_subcorpus = re.compile("form_[a|b]_[0-9][0-9][0-9]")
    path_pattern = os.path.join(destination_folder,'regesten/urn:cts:formulae:*_regesten.xml')
    regesten_identified = glob(path_pattern)
    if len(regesten_identified) ==0:
        logger.error("There are no regests in this directory. This will produces errors in later steps.")
    for soup_file in regesten_identified:
        with open(soup_file) as fp:
            doc_ids=[]
            soup = BeautifulSoup(fp, 'xml')
            parsable_docids = []
            for link in soup.find_all('regest'):
                doc_ids.append(link.get('docId'))
            if 0==len(doc_ids):
                logger.error('No docId found in '+str(soup_file))
            else:
                for doc_id in doc_ids:
                    malformed_doc_ids=False
                    # e.g., <regest docId="urn:cts:formulae:auvergne.form001"> --> ['urn','cts','formulae','auvergne.form001']
                    # <regest docId="urn:cts:formulae:sens.form_a_006">
                    doc_id_components = doc_id.split(':')
                    if 4 == len(doc_id_components):
                        #e.g., ['urn','cts','formulae','auvergne.form001'] -> ['auvergne', 'form001']
                        doc_id_title_components = doc_id_components[-1].split('.')
                        if 2 == len(doc_id_title_components):
                            if formel_number_pattern.match(doc_id_title_components[1]):
                                formel_number = doc_id_title_components[1].replace('form','')
                            elif formel_number_pattern_with_subcorpus.match(doc_id_title_components[1]):
                                formel_number = doc_id_title_components[1].split('_')[-1].replace('form','')
                            else:
                                logger.warning(str(doc_id_title_components)+' is malformed.')
                                formel_number = doc_id
                        else:
                            logger.warning(str(doc_id_title_components)+' is malformed.')
                            formel_number = doc_id
                    else:
                        logger.warning(doc_id+" is missing 'urn','cts' or 'formulae'")
                        formel_number = doc_id
                    if not docid_pattern_without_prefixes.match(formel_number):
                        malformed_doc_ids=True
                        logger.error('docId: '+formel_number+' is malformed.')
                    else:
                        parsable_docids.append(formel_number)
        if not malformed_doc_ids:
            logger.info('Regest files exists and is properly formatted at '+soup_file+'. It has the following docIds: '+str(parsable_docids))

def check_output_regesten_existance(corpus_folder:str, logger:logging.Logger, sampling_method:str='complete') -> bool:
    """
    Checks whether the transformed files having a capitains file with a proper a regest.
    Two different sampling methods:
        random: select random samples and print their names with the information on whether the regest exists or not
        complete: Checks all files and counts the number of proper regests.
    """
    sampling_method_options = ['random', 'complete']
    if sampling_method in sampling_method_options:
        subfolders = [ f.path for f in os.scandir(os.path.join(corpus_folder)) if f.is_dir() ]
        
        if 'random' == sampling_method:
            raise NotImplementedError()
        elif 'complete' == sampling_method:
            short_regesten_found = 0
            long_regest_found = 0
            for subfolder in subfolders:
                capitains_found = False
                for subsubpath in os.scandir(subfolder):
                    if "__capitains__.xml" == os.path.split(subsubpath)[-1]:
                        capitains_found = True
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(subsubpath)
                        root = tree.getroot()
                        for description in root.findall('.//{*}description'):
                            regesten_text = description.text
                            if regesten_text is not None:
                                if 0 < len(regesten_text):
                                    short_regesten_found += 1
                                    break
                            else:
                                ET.indent(description)
                                logger.debug("{} is empty {}".format(subsubpath.path, ET.tostring(description, encoding='unicode')))
                        
                        for abstract in root.findall('.//{*}abstract'):
                            regesten_text = abstract.text
                            if regesten_text is not None:
                                if 0 < len(regesten_text):
                                    long_regest_found += 1
                            else:
                                ET.indent(description)
                                logger.debug("{} is empty {}".format(subsubpath, ET.tostring(description, encoding='unicode')))
                if not capitains_found:
                    logger.debug(os.path.split(subsubpath))
                    logger.warning("No capitains file found in {}".format(subfolder))
            
            if short_regesten_found == len(subfolders) and long_regest_found == len(subfolders):
                logger.info("Success! All {} entries have a short regest and a long regest".format(short_regesten_found))
                return True
            elif short_regesten_found == len(subfolders): 
                logger.error("All entries have short regests but only {} of all {} entries have long regests, but all of them should have one.".format(long_regest_found, len(subfolders)))
                return False
            elif long_regest_found == len(subfolders): 
                logger.error("All entries have long regests but only {} of all {} entries have short regests, but all of them should have one.".format(short_regesten_found, len(subfolders)))
                return False
            else:
                logger.error("Only {} short regests and {} long regests for {} entries. But each entry should have  one short and one long regest.".format(long_regest_found, short_regesten_found, len(subfolders)))
                return False
    else:
        raise ValueError("{} is not a valid value for sampling_method. Please one of these options: {}".format(sampling_method, sampling_method_options))