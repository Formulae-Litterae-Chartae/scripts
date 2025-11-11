from util import get_logger, subprocess_run, make_proper_path, convert_docx_to_tei
import os
import argparse
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

def get_corpus_information(input_tei_path)-> dict:
    corpus_information_dict = {}

    _, file= os.path.split(input_tei_path)
    file_name = file.split(".")[0]
    file_parts = file_name.split(" ")

    if len(file_parts) == 3 or len(file_parts) == 2:
        corpus_information_dict["corpus"] = file_parts[1].lower()
        if len(file_parts) == 3:
            corpus_information_dict["subcorpus_index"] = file_parts[2].lower()
        else:
            corpus_information_dict["subcorpus_index"] = ""
        return corpus_information_dict
    else:
        raise ValueError("{} has a wrong file name".format(input_tei_path))
    
def create_subtrees(input_tei_path_list: list[str], logger) -> tuple[str, list, list]:
    if input_tei_path_list == []: raise ValueError('input_tei_path_list should not be empty') 
    xml_trees: list[ET[Element[str]]] = []
    output_paths:list[str] = []
    for input_tei_path in input_tei_path_list:
        corpus_information_dict = get_corpus_information(input_tei_path)
        corpus_name = corpus_information_dict["corpus"]
        if corpus_information_dict["subcorpus_index"]=='': 
            subcorpus_name = "_a"
        else:
            subcorpus_name = "_"+corpus_information_dict["subcorpus_index"]+"_"

        output_path = make_proper_path("~/git/scripts/formel_transform/output/{corpus}/regesten/urn:cts:formulae:{corpus}{subcorpus}regesten.xml".format(corpus=corpus_name, subcorpus=subcorpus_name))
        
        subprocess_run(commands=['java', '-jar',  saxon_location, '-s:{}'.format(input_tei_path), '-o:{}'.format(output_path), transformation_file], logger=logger)
        logger.info("Success! {} was converted to {} and then transformed to {} ".format(input_docx_path, input_tei_path, output_path))
        output_paths.append(output_path)
    
    
        tree = ET.parse(output_path)
        root = tree.getroot()
        for child in root:
            if "regest" == child.tag:
                if "docId" in child.attrib.keys():
                    if 'bourges' in corpus_name:
                        child.set('docId', "urn:cts:formulae:{corpus}.form{subcorpus}{form_num}".format(corpus=corpus_name, 
                                                                                            subcorpus=subcorpus_name,
                                                                                            form_num=child.get('docId')))
                    else: 
                        child.set('docId', "urn:cts:formulae:{corpus}.form{subcorpus}{form_num}".format(corpus=corpus_name, 
                                                                                                                    subcorpus=subcorpus_name,
                                                                                                                    form_num=child.get('docId')))
        xml_trees.append(tree)
    return corpus_name, xml_trees, output_paths

def remove_files(list_of_files:list[str], logger):
    for file_path in list_of_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug("{} was removed".format(file_path))
        else:
            logger.debug("{} does not exist. So, it could not be removed".format(file_path))

import glob
import os

def get_regesten_files(collection: str, collection_title_case: str, file_type: str='docx') -> list[str]:
    """
    Returns a list of XML files matching the pattern:
    ~/git/scripts/formel_transform/input/{collection}/Regesten {collection_title_case} [A|B|I|II|...].xml

    :param collection: The lowercase collection name (e.g., 'sens')
    :param collection_title_case: The title-case version (e.g., 'Sens')
    :return: A list of matching file paths
    """
    base_dir = os.path.expanduser(f"~/git/scripts/formel_transform/input/{collection}")
    #pattern = f"Regesten {collection_title_case} [ABI]*.{file_type}"
    pattern = f"Regesten {collection_title_case}*.{file_type}"
    search_path = os.path.join(base_dir, pattern)
    return sorted(glob.glob(search_path))


# python3 ~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.py
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Script to transform DOCX files with regesten to a correspondig tei file")
    parser.add_argument('-preserve_temp_files', action='store_true', 
                        help="All temporarily created files should be preserved. If this flag is not set, they are deleted by default.")
    parser.add_argument('-c', '--collection', required=True,
                    help="Collection, that you want to ingest the regesten")
    args=parser.parse_args()
    default_saxon_location = make_proper_path("~/Downloads/SaxonHE9-8-0-11J/saxon9he.jar")
    logger = get_logger()
    logger.setLevel('DEBUG')
    saxon_location = default_saxon_location
    collection = args.collection
    collection_title_case = collection.title()
    transformation_file =  make_proper_path("~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.xsl")
    #input_docx_path = make_proper_path("~/git/scripts/formel_transform/input/{}/Regesten {} A.docx".format(collection, collection_title_case))
    input_docx_path_list = get_regesten_files(collection, collection_title_case)
    logger.info("Found regesten files: {} for {}".format(input_docx_path_list, collection))
    input_tei_path_list:list[str] = list()
    for input_docx_path in input_docx_path_list:
        tei_path = input_docx_path.replace('docx', 'xml')
        convert_docx_to_tei(input_docx_path, tei_path, logger=logger)
        input_tei_path_list.append(tei_path)
    
    print(input_tei_path_list)
    

    corpus_name, xml_trees, output_paths = create_subtrees(input_tei_path_list=input_tei_path_list, 
                            logger=logger)
    
    if 0 == len(xml_trees): raise FileNotFoundError('No tree found')

    
    main_tree: ET = xml_trees[0]
    main_root = xml_trees[0].getroot()
    if 1 < len(xml_trees):
        # extend the first tree with all other trees
        for tree in xml_trees[1:]:
            additional_root = tree.getroot()
            main_root.extend(additional_root)
        
    ET.indent(main_tree, space='  ', level=0)
    #print(ET.tostring(root, encoding='utf8'))
    final_output_path = make_proper_path("~/git/scripts/formel_transform/output/{corpus}/regesten/urn:cts:formulae:{corpus}_regesten.xml".format(corpus=corpus_name))
    with open(final_output_path, 'w', encoding='UTF-8') as final_output_file:
        main_tree.write(final_output_file, encoding='unicode')
    if os.path.isfile(final_output_path):
        logger.info("Success! All regests from {} are converted to {} ".format(corpus_name, final_output_path))
    else:
        logger.info("FAILURE! {} was not created.".format(final_output_path))
    if not args.preserve_temp_files:
        remove_files(output_paths,logger)