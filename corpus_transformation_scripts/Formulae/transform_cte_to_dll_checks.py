from glob import glob
from bs4 import BeautifulSoup
import os
import re 
import logging
import xml.etree.ElementTree as ET
from util import make_proper_path
from lxml import etree

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
    # This is a list of id that are ignored by the xslt process
    known_exceptions = ['#w3']
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
        # logger.error('Not all notes where transformed from {} ({}) to {} ({})'.format(input_file, 
        #                                                                                 input_apparatus_notes_unique_target_ends,
        #                                                                                 transformed_file,
        #                                                                                 transformed_apparatus_notes_unique_target_ends))
        logger.error('The notes: {} where not transformed from {} to {}. '.format(input_apparatus_notes_unique_target_ends-transformed_apparatus_notes_unique_target_ends,
            input_file, transformed_file))
        
def check_transcriptions_got_proper_names(manuscript:str, transcription_path: str, logger:logging.Logger) -> bool:
    tree = ET.parse(transcription_path)
    root = tree.getroot()
    all_checks_passed = True
    #   <text>
    #  <body>
    #     <div type="edition"
    #          xml:lang="lat"
    #          n="urn:cts:formulae:p14.47r48v.lat001"
    #          subtype="transcription">
    # /tei:TEI/tei:text/tei:body/tei:div/@n
    proper_name_found = False
    transcription_elements = root.findall('.//*[@subtype="transcription"]')
    if 1 > len(transcription_elements): 
        raise ValueError("No transcription found")
    
    for div in transcription_elements:
        path_pattern_string = "urn:cts:formulae:"+manuscript+"\.[\w\d]*\.lat001"
        path_pattern = re.compile(path_pattern_string)
        extracted_path = div.get("n")
        if not path_pattern.match(extracted_path):
            raise ValueError("{} does not met the pattern: {}".format(extracted_path, path_pattern_string))
        else:
            logger.debug("Found proper transcription name: {}".format(extracted_path))
            proper_name_found = True 
    
    return proper_name_found

def check_paths_in_capitains(capitains_path:str, logger:logging.Logger) -> bool:
    """
    """
    
    tree = ET.parse(capitains_path)
    root = tree.getroot()
    all_checks_passed = True
    for collection in root.findall('.//{*}collection'):
        extracted_path = collection.get('path')
        # this case applies for all transcriptions
        # Example of a valid transcription entry:
        # <collection path="../../p14/47r48v/__capitains__.xml" identifier="urn:cts:formulae:p14.47r48v"/>
        if 'form' not in extracted_path:
            collection_string = ET.tostring(collection)
            if "identifier" not in collection.keys():
                logger.error("{} has no identifier. This means there was an error in the processing. ".format(capitains_path))
                all_checks_passed = False
            else:
                extracted_identifier = collection.get("identifier")
                extracted_path_components = extracted_path.split('/')
                if 3 > len(extracted_path_components):
                    logger.error("Path has not enough components: {}".format(extracted_path_components))
                    all_checks_passed = False
                    break
                expected_identifier = "urn:cts:formulae:{}.{}".format(extracted_path_components[-3],extracted_path_components[-2])
                if extracted_identifier != expected_identifier:
                    logger.error("The identifier: {} should look like this {} based on {}".format(extracted_identifier, expected_identifier, capitains_path))
            
            extracted_path_manipulated =  make_proper_path(extracted_path.replace("../../",""))
            if not os.path.isfile(extracted_path_manipulated):
                logger.debug("{} from {} does not exist. This means there was an error in the processing. ".format(extracted_path_manipulated, capitains_path))
                all_checks_passed = False
    return all_checks_passed


def check_if_collection_exists(collection_id:str, collection_type:str, path_to_corpora="/home/thorben.schomacker/git/formulae-corpora/data", raise_errors=False) -> bool:
    """
    All collections (including transcriptions) do need to have:
        one folder with in the formulae-corpora directory with a capitains file and 
        one entry in the corresponding overall capitains file (e.g., formulae-corpora/data/manuscript_collection/__capitains__.xml)
    If both conditions are met  -> True
    Otherwise                   -> False
    """

    collection_path = os.path.join(path_to_corpora, collection_id)
    if os.path.isdir(collection_path):
        capitains_path= os.path.join(collection_path, "__capitains__.xml")
        if os.path.isfile(capitains_path):
            if collection_type == "transcription":
                collection_of_collections_path = os.path.join(path_to_corpora, 'manuscript_collection', '__capitains__.xml')
            else:
                raise ValueError(collection_type+" is not a valid collection type.")    
            
            
            ns = {'dct': "http://purl.org/dc/terms/", 'dc': "http://purl.org/dc/elements/1.1/", 'cpt': "http://purl.org/capitains/ns/1.0#", 'tei': 'http://www.tei-c.org/ns/1.0'}

            collection_of_collections = etree.parse(collection_of_collections_path)
            
            #for collection_id in collection_of_collections.xpath("/cpt:collection/cpt:members/cpt:collection[identifier='urn:cts:formulae:{}']".format(collection_id), namespaces=ns):
            list_of_identifiers = []
            # For more information on the naming conventions please visit: https://formulae-litterae-chartae.github.io/formulae-capitains-nemo/naming 
            identifier_pattern_string = "urn:cts:formulae:"+collection_id+"s*"
            identifier_pattern = re.compile(identifier_pattern_string)

            for collection in collection_of_collections.xpath("/cpt:collection/cpt:members/cpt:collection", namespaces=ns):
                identifier = collection.get('identifier')
                if identifier_pattern.match(identifier):
                    return True
                else:
                    list_of_identifiers.append(identifier)
            raise ValueError("{} not found in the list identifiers - {} -  from {}".format(collection_id, list_of_identifiers,collection_of_collections))

        else:
            if raise_errors: raise FileNotFoundError("{} does not exist. This will cause errors later.".format(capitains_path))
            return False
    else:
        if raise_errors: raise FileNotFoundError("{} does not exist. This will cause errors later.".format(collection_path))
        return False
                



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
            no_short_regest = []
            for subfolder in subfolders:
                capitains_found = False
                for subsubpath in os.scandir(subfolder):
                    if "__capitains__.xml" == os.path.split(subsubpath)[-1]:
                        capitains_found = True
                        short_regesten_found_in_capitains = False
                        import xml.etree.ElementTree as ET
                        tree = ET.parse(subsubpath)
                        root = tree.getroot()
                        for description in root.findall('.//{*}description'):
                            regesten_text = description.text
                            if regesten_text is not None:
                                if 0 < len(regesten_text):
                                    short_regesten_found += 1
                                    short_regesten_found_in_capitains = True
                                    break
                            else:
                                ET.indent(description)
                                logger.debug("{} is empty {}".format(subsubpath.path, ET.tostring(description, encoding='unicode')))
                        # a capitains, can have multiple description elements
                        # If at least has text, all others will also mostly have texts
                        if short_regesten_found_in_capitains:
                            #short_regesten_found +=1
                            pass
                        else:
                            no_short_regest.append(os.path.split(subsubpath)[-2])
                        for abstract in root.findall('.//{*}abstract'):
                            regesten_text = abstract.text
                            if regesten_text is not None:
                                if 0 < len(regesten_text):
                                    long_regest_found += 1
                                    break
                            else:
                                ET.indent(description)
                                logger.debug("{} is empty {}".format(subsubpath, ET.tostring(description, encoding='unicode')))
                if not capitains_found:
                    logger.debug(os.path.split(subsubpath))
                    logger.warning("No capitains file found in {}".format(subfolder))
            
            if short_regesten_found == len(subfolders) and long_regest_found == len(subfolders):
                logger.info("Success! All {} entries have exactly one short regest and one long regest".format(short_regesten_found))
                print("Success! All {} entries have exactly one short regest and one long regest".format(short_regesten_found))
                return True
            else:
                if short_regesten_found == len(subfolders) and long_regest_found != len(subfolders): 
                    logger.error("All entries have short regests but only {} of all {} entries have long regests, but all of them should have one.".format(long_regest_found, len(subfolders)))
                if short_regesten_found != len(subfolders) and long_regest_found == len(subfolders): 
                    logger.error("All entries have long regests but only {} of all {} entries have short regests, but all of them should have one.".format(short_regesten_found, len(subfolders)))
                    logger.error("{} have no short regest".format(no_short_regest))
                if short_regesten_found != len(subfolders) and long_regest_found != len(subfolders):
                    logger.error("Only {} short regests and {} long regests for {} entries. But each entry should have  one short and one long regest.".format(long_regest_found, short_regesten_found, len(subfolders)))
                    logger.error("{} have no short regest".format(no_short_regest))

                return False
    else:
        raise ValueError("{} is not a valid value for sampling_method. Please one of these options: {}".format(sampling_method, sampling_method_options))
    
def check_hss_editionen_file(hss_editionen_file_path:str, logger:logging.Logger) -> bool:
    forbidden_strings_regex = "[<|>]*amp"
    hss_editionen = etree.parse(make_proper_path(hss_editionen_file_path))
    formula_with_proper_n_element = 0
    formula_with_proper_text = 0

    formula_list = hss_editionen.xpath("/xml/formula")

    for formula in formula_list:
        if "n" in formula.keys():
            n_str = formula.get('n')
            formula_with_proper_n_element +=1
        formula_text = formula.text
        if not re.search(forbidden_strings_regex, formula_text):
            formula_with_proper_text +=1
    
    if (len(formula_list) == formula_with_proper_text) and (len(formula_list) == formula_with_proper_n_element):
        logger.info("Found {} formula entries. All have proper n-attributes and texts.".format(formula_with_proper_text))
        return True
    else:
        logger.warning("Found {} formula entries. Only {} have proper n-attributes and {} have proper texts.".format(len(formula_list), formula_with_proper_n_element, formula_with_proper_text))

import re
def check_fols(fols: str, logger:logging.Logger) -> bool:
    """
    Checks whether the given string matches the expected folio range pattern.

    Valid formats include:
        - "12r13v"
        - "45bisr67bisv"
        - "3v5r"

    Returns:
        bool: True if the format is valid, otherwise raises ValueError.

    Raises:
        ValueError: If the input does not match the expected folio pattern.
    """
    pattern_str = r"(\d{1,3}(bis)?[r|v][a|b]?){1,2}"

    if not re.fullmatch(pattern_str, fols):
        logger.error(f"{fols} does not match the naming pattern for transcriptions.")
        raise ValueError(f"{fols} does not match the naming pattern for transcriptions.")
        return False
    else:
        return True
