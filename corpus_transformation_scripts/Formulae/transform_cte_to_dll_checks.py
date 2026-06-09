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
        if not('form' in extracted_path or 'capitula' in extracted_path or 'incipit' in extracted_path):
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
    marculf_docid_pattern_without_prefixes = re.compile("form_I{1,2}_[0-9]+") #e.g., <regest docId="001">
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
                    if not marculf_docid_pattern_without_prefixes.match(formel_number):
                        malformed_doc_ids=True
                        logger.error('docId: '+formel_number+' in '+ soup_file +' does not match the pattern: '+str(docid_pattern_without_prefixes))
                    elif not docid_pattern_without_prefixes.match(formel_number):
                        malformed_doc_ids=True
                        logger.error('docId: '+formel_number+' in '+ soup_file +' does not match the pattern: '+str(docid_pattern_without_prefixes))
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
def check_fols(man:str, fols: str, logger:logging.Logger) -> bool:
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

    if "sg2" == man:
        print("sg2 found")
        if re.fullmatch(r"\d{2,4}", man):
            return True
    elif not re.fullmatch(pattern_str, fols):
        logger.error(f"{man}.{fols} does not match the naming pattern for transcriptions.")
        #raise ValueError(f"{man}.{fols}  does not match the naming pattern for transcriptions.")
    else:
        return True

def check_empty_notes():
    # should check whether there are any empty notes. They look like this:
    # <note type="n1" place="right"><p xml:space="preserve"/></note>
    raise NotImplementedError

#############################################
# leaked apartus notes
def _get_tei_ns() -> dict[str, str]:
    """
    Namespace mapping for TEI XPath queries.
    """
    return {"tei": "http://www.tei-c.org/ns/1.0"}


def _normalize_whitespace(text: str | None) -> str:
    """
    Collapse repeated whitespace for log-friendly output.
    """
    if text is None:
        return ""
    return " ".join(text.split())


def _get_nearest_paragraph_id(elem) -> str | None:
    """
    Return the xml:id of the closest ancestor paragraph, if available.
    """
    ns = _get_tei_ns()
    paragraph = elem.xpath("ancestor::tei:p[1]", namespaces=ns)
    if paragraph:
        return paragraph[0].get("{http://www.w3.org/XML/1998/namespace}id")
    return None


def _serialize_xml_snippet(elem, max_length: int = 500) -> str:
    """
    Serialize an element to a compact single-line XML snippet for logging.
    """
    snippet = etree.tostring(elem, encoding="unicode", with_tail=False)
    snippet = snippet.replace("\n", " ")
    return snippet[:max_length]


def _extract_leaked_apparatus_context(mentioned_elem) -> dict[str, str | None]:
    """
    Extract structured context for a suspicious <mentioned> element that occurs
    outside a <note>.
    """
    paragraph_id = _get_nearest_paragraph_id(mentioned_elem)
    mentioned_text = _normalize_whitespace("".join(mentioned_elem.itertext()))

    next_note_begin_marker = mentioned_elem.xpath(
        "following::tei:seg[@type='note-begin-marker'][1]",
        namespaces=_get_tei_ns()
    )

    next_marker_id = None
    next_marker_text = None
    if next_note_begin_marker:
        next_marker = next_note_begin_marker[0]
        next_marker_id = next_marker.get("{http://www.w3.org/XML/1998/namespace}id")
        next_marker_text = _normalize_whitespace("".join(next_marker.itertext()))

    parent_snippet = None
    parent = mentioned_elem.getparent()
    if parent is not None:
        parent_snippet = _serialize_xml_snippet(parent)

    return {
        "paragraph_id": paragraph_id,
        "mentioned_text": mentioned_text,
        "next_marker_id": next_marker_id,
        "next_marker_text": next_marker_text,
        "parent_snippet": parent_snippet,
    }


def check_leaked_apparatus_in_text(
    transformed_file: str,
    logger: logging.Logger,
    raise_errors: bool = False
) -> bool:
    """
    Check whether apparatus material has leaked into the running text.

    This specifically detects <mentioned> elements that occur outside <note>,
    which is a strong indicator that note content was serialized into the text
    instead of remaining fully enclosed in the apparatus note.

    Args:
        transformed_file: Path to the transformed TEI XML file.
        logger: Logger instance.
        raise_errors: If True, raise ValueError when suspicious cases are found.

    Returns:
        bool: True if no suspicious cases were found, False otherwise.
    """
    parser = etree.XMLParser(remove_blank_text=False, recover=True)

    try:
        tree = etree.parse(transformed_file, parser)
    except Exception as exc:
        logger.error("Could not parse %s: %s", transformed_file, exc)
        if raise_errors:
            raise
        return False

    ns = _get_tei_ns()
    leaked_mentions = tree.xpath(
        "//tei:mentioned[not(ancestor::tei:note)]",
        namespaces=ns
    )

    if not leaked_mentions:
        logger.debug("Check passed! No leaked apparatus material found in %s.",transformed_file)
        return True

    logger.error(
        "Check FAILED! Found %s suspicious <mentioned> element(s) outside <note> in %s.",
        len(leaked_mentions),
        transformed_file,
    )

    for i, mentioned_elem in enumerate(leaked_mentions, start=1):
        context = _extract_leaked_apparatus_context(mentioned_elem)

        logger.error(
            (
                "[%s] Suspicious leaked apparatus in %s | paragraph=%s | "
                "mentioned=%r | next_note_begin_marker=%s | next_marker_text=%r | "
                "parent_snippet=%s"
            ),
            i,
            transformed_file,
            context["paragraph_id"],
            context["mentioned_text"],
            context["next_marker_id"],
            context["next_marker_text"],
            context["parent_snippet"],
        )

    if raise_errors:
        raise ValueError(
            f"Found {len(leaked_mentions)} suspicious <mentioned> element(s) "
            f"outside <note> in {transformed_file}."
        )

    return False

def check_leaked_apparatus_in_corpus(
    corpus_folder: str,
    logger: logging.Logger,
    raise_errors: bool = False
) -> bool:
    """
    Run the leaked apparatus check on all XML files in a corpus folder.
    """
    xml_files = glob(os.path.join(corpus_folder, "**", "*.xml"), recursive=True)

    if not xml_files:
        logger.warning("No XML files found in %s.", corpus_folder)
        return True

    logger.info("Checking %s XML files in %s...", len(xml_files), corpus_folder)

    all_checks_passed = True

    for xml_file in xml_files:
        passed = check_leaked_apparatus_in_text(
            xml_file,
            logger,
            raise_errors=False
        )
        if not passed:
            all_checks_passed = False

    if all_checks_passed:
        logger.info("All files passed leaked apparatus check.")
    else:
        logger.error("Leaked apparatus detected in corpus.")

    if not all_checks_passed and raise_errors:
        raise ValueError(
            f"Leaked apparatus material found in one or more XML files under {corpus_folder}."
        )

    return all_checks_passed

#############################################
# Make it console executable

def _setup_default_logger() -> logging.Logger:
    """
    Create a simple console logger if none is provided.
    """
    logger = logging.getLogger("cte_checks_cli")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


if __name__ == "__main__":
    import sys

    logger = _setup_default_logger()

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tranform_cte_to_dll_checks.py <command> [args]")
        print("")
        print("Available commands:")
        print("  check_leaked_apparatus_in_corpus <corpus_folder>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "check_leaked_apparatus_in_corpus":
        if len(sys.argv) < 3:
            print("Missing argument: corpus_folder")
            sys.exit(1)
        if len(sys.argv) > 3: 
            if sys.argv[3].lower() == "debug":
                logger.setLevel(logging.DEBUG)
        
        corpus_folder = sys.argv[2]
        
        success = check_leaked_apparatus_in_corpus(
            corpus_folder,
            logger,
            raise_errors=False
        )

        if not success:
            sys.exit(2)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)