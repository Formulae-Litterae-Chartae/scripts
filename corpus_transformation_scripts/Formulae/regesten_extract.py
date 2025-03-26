from util import get_logger, subprocess_run, make_proper_path, convert_docx_to_tei
import os
import argparse
import xml.etree.ElementTree as ET

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
    
def create_subtrees(input_tei_path_list: list[str], logger):
    xml_trees = []
    output_paths = []
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

# python3 ~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.py
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Script to transform DOCX files with regesten to a correspondig tei file")
    parser.add_argument('-preserve_temp_files', action='store_true', 
                        help="All temporarily created files should be preserved. If this flag is not set, they are deleted by default.")
    args=parser.parse_args()
    default_saxon_location = make_proper_path("~/Downloads/SaxonHE9-8-0-11J/saxon9he.jar")
    logger = get_logger()
    logger.setLevel('DEBUG')
    saxon_location = default_saxon_location
    transformation_file =  make_proper_path("~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.xsl")
    input_docx_path = make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.docx")

    try:
        input_tei_path = convert_docx_to_tei(input_docx_path)
    except NotImplementedError:
        logger.warning('please implement convert_docx_to_tei()')
        input_tei_path = make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.xml")
    
    

    corpus_name, xml_trees, output_paths = create_subtrees([make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.xml"), 
                           make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens B.xml")], logger=logger)
    # tree_two = ET.parse(output_paths[1])
    # root_two = tree_two.getroot()
    # for child in root_two:
    #     if "regest" == child.tag:
    #         if "docId" in child.attrib.keys():
    #             child.set('docId', "urn:cts:formulae:{corpus}.form{subcorpus}{form_num}".format(corpus=corpus_name, 
    #                                                                                                         subcorpus=subcorpus_name,
    #                                                                                                         form_num=child.get('docId')))
    #             print(child.get('docId'))
    if 1 < len(xml_trees):
        main_tree = xml_trees[0]
        main_root = xml_trees[0].getroot()
        # extend the first tree with all other trees
        for tree in xml_trees[1:]:
            additional_root = tree.getroot()
            main_root.extend(additional_root)
        
    ET.indent(main_tree, space='  ', level=0)
    #print(ET.tostring(root, encoding='utf8'))
    final_output_path = make_proper_path("~/git/scripts/formel_transform/output/{corpus}/regesten/urn:cts:formulae:{corpus}_regesten.xml".format(corpus=corpus_name))
    main_tree.write(final_output_path)
    logger.info("Success! All regests from {} are converted to {} ".format(corpus_name, final_output_path))
    if not args.preserve_temp_files:
        remove_files(output_paths,logger)