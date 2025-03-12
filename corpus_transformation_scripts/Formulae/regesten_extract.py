from util import get_logger, subprocess_run, make_proper_path, convert_docx_to_tei
import os
import argparse

def get_corpus_information(input_tei_path)-> dict:
    corpus_information_dict = {}

    _, file= os.path.split(input_tei_path)
    file_name = file.split(".")[0]
    file_parts = file_name.split(" ")

    if len(file_parts) == 3 or len(file_parts) == 2:
        corpus_information_dict["corpus"] = file_parts[1].lower()
        if len(file_parts) == 3:
            corpus_information_dict["subcorpus_index"] = file_parts[2]
        else:
            corpus_information_dict["subcorpus_index"] = ""
        return corpus_information_dict
    else:
        raise ValueError("{} has a wrong file name".format(input_tei_path))


# python3 ~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.py
if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Script to transform DOCX files with regesten to a correspondig tei file")
    default_saxon_location = make_proper_path("~/Downloads/SaxonHE9-8-0-11J/saxon9he.jar")
    logging = get_logger()
    saxon_location = default_saxon_location
    transformation_file =  make_proper_path("~/git/scripts/corpus_transformation_scripts/Formulae/regesten_extract.xsl")
    input_docx_path = make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.docx")

    try:
        input_tei_path = convert_docx_to_tei(input_docx_path)
    except NotImplementedError:
        logging.warning('please implement convert_docx_to_tei()')
        input_tei_path = make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.xml")
    for input_tei_path in [make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens A.xml"), 
                           make_proper_path("~/git/scripts/formel_transform/input/sens/Regesten Sens B.xml")]:
        subcorpus_name=''
        corpus_information_dict = get_corpus_information(input_tei_path)
        corpus_name = corpus_information_dict["corpus"]
        if corpus_information_dict["subcorpus_index"]!='': subcorpus_name = "_a"

        output_path = make_proper_path("~/git/scripts/formel_transform/output/{corpus}/data/regesten/urn:cts:formulae:{corpus}{subcorpus}_regesten.xml".format(corpus=corpus_name, subcorpus=subcorpus_name))
        
        subprocess_run(commands=['java', '-jar',  saxon_location, '-s:{}'.format(input_tei_path), '-o:{}'.format(output_path), transformation_file], logging=logging)
        logging.info("Success! {} was converted to {} and then transformed to {} ".format(input_docx_path, input_tei_path, output_path))