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
                          {"url":"https://gallica.bnf.fr/ark:/12148/btv1b52515201k", 
                           # holds the number of 'empty' pages before the 'real' folios start
                           "overhead":10}
                          }



def _get_page_number(image_id:str, transcription_collection_id:str) -> int:
    
    folio_number = int(re.sub(r'[r|v]','',image_id))
    # corrects the shift in in th page enumeration during the digitization
    folio_number = folio_number + manuscript_information[transcription_collection_id]['overhead'] + folio_number-1
    # pages with an v are on the 'right' side so their page number is 1 higher than their left-handed counterparts
    if 'v' in image_id: folio_number += 1
    return folio_number

def _make_images_dict(title_urn:str, logger:logging.Logger) -> dict[str:str]:
    """Function that creates a dict, that holds url to the manuscript images.
    Every URL is checked beforehand and only included if it returns content.

    Args:
        title_urn: 
        logger: 

    Returns:
        A dict similar to this:
        {'images': 
            {<folio number>: <url to the manuscript image>}
        }

    """

    #title_from_xml = re.sub(".+lat \[fol\.", "", title_from_xml)
    #title_from_xml = re.sub("<span.+", "", title_from_xml)
    title_parts = title_urn.replace("urn:cts:formulae:",'').split('.')
    transcription_collection_id = title_parts[0]

    images_dict = dict()
    for folio_id in re.findall(r'\d+[r|v]', title_parts[1]):
        page_number = _get_page_number(folio_id, transcription_collection_id)
        
        folio_url = manuscript_information[transcription_collection_id]['url']+"/canvas/f"+str(page_number)
        response = requests.get(folio_url)
        if response.status_code == requests.codes.ok:
            images_dict[folio_id] = folio_url
        else:
            logger.warning("{} from {}".format(response.status_code, folio_url))
    return images_dict



def main(data_folder:str,output_folder:str, logger) -> dict[str:list[dict[str:str]]]:
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
            for transcription in tqdm(os.listdir(os.path.join(data_folder, collection_id)),desc="Text(s) from "+collection_id): 
                transcription_folder_path = os.path.join(data_folder, collection_id, transcription)
                if os.path.isdir(transcription_folder_path):
                    for file in os.listdir(transcription_folder_path):
                        if fnmatch.fnmatch(file, '*.lat001.xml'):
                            file_path = os.path.join(transcription_folder_path, file)
                            #<div type="edition" xml:lang="lat" n="urn:cts:formulae:p12.2r2v.lat001" subtype="transcription">
                            title_from_xml = etree.parse(file_path).xpath('//tei:title[not(@type)]/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
                            title_urn = etree.parse(file_path).xpath('//tei:div[@subtype="transcription"]/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})[0]
                            result_dict = {
                                            "title": title_urn,
                                            "codex_name": (title_from_xml).split("lat [f")[0],
                                            "manifest_link": manuscript_information[collection_id]['url']+"/manifest.json", 
                                            "images": _make_images_dict(title_urn, logger)
                                            }
                            transcription_dict_list.append(result_dict)
            collections[collection_id] = transcription_dict_list
    
            
            with open(os.path.join(output_folder, collection_id+".json"), 'w') as file:
                file.write(json.dumps(transcription_dict_list, indent=4))
    return collections

# python3 ~/git/scripts/corpus_transformation_scripts/Formulae/generate_iiif_json.py -h
if __name__ == "__main__":
    parser=argparse.ArgumentParser(description="Script to to create a IIIF ingestion json file for manuscript images."
                                   "Please note, that this method relies on adding the url and overhead information manually."
                                   "Once this is done everything else should happen automatically.")
    parser.add_argument("--input_folder","-i", type=str,default='~/git/scripts/formel_transform/output/sens/data', 
                        help='Folder with the transcription files.')
    parser.add_argument("--output_folder","-o", type=str,default='~/git/scripts/formel_transform/output/sens/iiif', 
                        help='Folder for the resultung json files.')
    parser.add_argument("--logging_level","-l", type=str, help="Logging level", default="DEBUG")
    args=parser.parse_args()

    # Turn of the debugging messages from requests (https://stackoverflow.com/a/11029841/7924573)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = get_logger()
    logger.setLevel(args.logging_level)
    main(args.input_folder, args.output_folder, logger)