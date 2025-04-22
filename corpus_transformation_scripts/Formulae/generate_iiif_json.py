from util import make_proper_path, get_logger
import os
import fnmatch
from lxml import etree
import re
import requests
from tqdm import tqdm
import logging
import json
import argparse

manuscript_information = {"p12": 
                          {
                            "manifest":"https://gallica.bnf.fr/iiif/ark:/12148/btv1b52515201k/manifest.json"
                          },
                          "m4": 
                          {
                            "manifest":"https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00071101/manifest"
                          },
                        }
# ??? m1 = https://www.bavarikon.de/object/bav:ASM-EMM-00000BAV80001988?p=21&lang=de

def _create_folio_id_url_map(manifest_url:str) -> dict[str, str]:
    # only create a dict for supported libraries
    if 'gallica' in manifest_url:
        folio_id_url_map = dict()
        response = requests.get(manifest_url)
        manifest_json = response.json()
        for canvas in manifest_json["sequences"][0]["canvases"]:
            folio_id_url_map[canvas["label"]] = canvas["@id"]
        return folio_id_url_map
    else:
        return None

def _make_images_dict(folio_id_url_map,  title_urn:str, logger:logging.Logger) -> dict[str:str]:
    """Function that creates a dict, that holds url to the manuscript images.
    Every URL is checked beforehand and only included if it returns content.

    Args:
        title_urn: 
        logger: 

    Returns:
        A dict similar to this:
        {'images': 
            {<folio id>: <url to the manuscript image>}
        }

    """
    
    title_parts = title_urn.replace("urn:cts:formulae:",'').split('.')

    folio_ids = re.findall(r'\d+[r|v]', title_parts[1])
    if folio_ids == []: raise ValueError("No folio ids found in "+title_urn)

    images_dict = dict()
    if folio_id_url_map is None:
        raise NotImplementedError('Automatic extraction of images_dict for this data is not yet supported.')
    else:
        for folio_id in folio_ids:
            images_dict[folio_id] = folio_id_url_map[folio_id]
    return images_dict


def _append_to_existing_json(transcription_dict_list:dict[str:str], corpora_folder:str, collection_id:str, logger:logging.Logger) -> dict[str:str]:
    """
    Merges an a newly created iiif json file with an existing one for the same manuscript collection. 
    """
    collection_id_capitalize = collection_id.capitalize()
    if corpora_folder != "":
        existing_json_file_path = os.path.join(corpora_folder, 'iiif', collection_id_capitalize+'.json')
        if os.path.isfile(existing_json_file_path):
            with open(existing_json_file_path) as existing_json_file:
                existing_json = json.load(existing_json_file)
            if collection_id_capitalize in existing_json.keys():
                existing_transcription_dicts = existing_json[collection_id_capitalize]
                transcription_dict_list = existing_transcription_dicts + transcription_dict_list
                logging.info("merged with "+existing_json_file_path)
                return transcription_dict_list
                
            else:
                logging.debug(collection_id_capitalize+" not found in "+existing_json_file_path)
        else:
            logging.debug("File not found: "+existing_json_file_path)
    return transcription_dict_list


def main(data_folder:str,output_folder:str, corpora_folder:str, logger) -> dict[str:list[dict[str:str]]]:
    """
    Parameter:
        transcription_folder
    """

    collections = dict()
    for collection_id in os.listdir(data_folder):
        transcription_dict_list = []
        if collection_id not in manuscript_information.keys():
            logger.warning(collection_id+" is not part of the catalog.")
        else:
            folio_id_url_map = _create_folio_id_url_map(manuscript_information[collection_id]['manifest'])
            #folio_id_url_map = _create_folio_id_url_map(manuscript_information[collection_id]['url']+"/manifest.json")
            for transcription in tqdm(os.listdir(os.path.join(data_folder, collection_id)),desc="Text(s) from "+collection_id): 
                transcription_folder_path = os.path.join(data_folder, collection_id, transcription)
                #transcription_folio_id_mismatches = list[tuple]

                if os.path.isdir(transcription_folder_path):
                    for file in os.listdir(transcription_folder_path):
                        if fnmatch.fnmatch(file, '*.lat001.xml'):
                            file_path = os.path.join(transcription_folder_path, file)
                            #<div type="edition" xml:lang="lat" n="urn:cts:formulae:p12.2r2v.lat001" subtype="transcription">
                            title_from_xml = etree.parse(file_path).xpath('//tei:title[not(@type)]/text()', 
                                                                          namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
                            title_urn = etree.parse(file_path).xpath('//tei:div[@subtype="transcription"]/@n', 
                                                                     namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
                            try:
                                images_dict = _make_images_dict(folio_id_url_map,  title_urn, logger)
                                #images_dict, folio_id_mismatches = _make_images_dict(title_urn, logger)
                                #transcription_folio_id_mismatches = transcription_folio_id_mismatches + folio_id_mismatches
                                result_dict = {
                                            "title": title_urn,
                                            "codex_name": (title_from_xml).split(" [f")[0],
                                            #"manifest_link": manuscript_information[collection_id]['url']+"/manifest.json", 
                                            "manifest_link": manuscript_information[collection_id]['manifest'], 
                                            "images": images_dict
                                            }
                                transcription_dict_list.append(result_dict)
                            except (ValueError, NotImplementedError) as error:
                                logging.exception("Unable to create a iff json entry for {}. Caused by {} {}".format(file, type(error).__name__, error))

            transcription_dict_list = _append_to_existing_json(transcription_dict_list, corpora_folder, collection_id, logger)
            
            collections[collection_id] = transcription_dict_list
            output_file_path = os.path.join(output_folder, collection_id+".json")
            with open(output_file_path, 'w') as file:
                main_json = {collection_id.capitalize() : transcription_dict_list}
                file.write(json.dumps(main_json, indent=4))
                logger.info("Exported to: "+output_file_path)
        

    return collections

# python3 ~/git/scripts/corpus_transformation_scripts/Formulae/generate_iiif_json.py -h
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Script to to create a IIIF ingestion json file for manuscript images."
                                   "Please note, that this method relies on adding the url and overhead information manually."
                                   "Once this is done everything else should happen automatically.")
    parser.add_argument("--input_folder","-i", type=str,default='~/git/scripts/formel_transform/output/sens/data', 
                        help='Folder with the transcription files.')
    parser.add_argument("--output_folder","-o", type=str,default='~/git/scripts/formel_transform/output/sens/iiif', 
                        help='Folder for the resulting json files.')

    parser.add_argument("--corpora_folder","-c", type=str,default='~/git/formulae-corpora', 
                        help='Folder which holds the formulae corpora. '
                        'If this attribute is set, existing iiif json files are merge with the new ones. the resulting json files.')
    parser.add_argument("--logging_level","-l", type=str, help="Logging level", default="DEBUG")
    args=parser.parse_args()

    # Turn of the debugging messages from requests (https://stackoverflow.com/a/11029841/7924573)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = get_logger()
    logger.setLevel(args.logging_level)
    main(make_proper_path(args.input_folder), make_proper_path(args.output_folder), make_proper_path(args.corpora_folder), logger)