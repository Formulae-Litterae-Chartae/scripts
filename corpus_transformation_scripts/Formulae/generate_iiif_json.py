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
                            "manifest":"https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00071101/manifest",
                            "overhead": 4,
                            "image_link":"https://api.digitale-sammlungen.de/iiif/presentation/v2/bsb00071101/canvas/",
                          },
                        }
# ??? m1 = https://www.bavarikon.de/object/bav:ASM-EMM-00000BAV80001988?p=21&lang=de

def _get_page_number(image_id:str, transcription_collection_id:str) -> int:
    folio_number = int(re.sub(r'[r|v]','',image_id))
    # corrects the shift in in th page enumeration during the digitization
    folio_number = folio_number + manuscript_information[transcription_collection_id]['overhead'] + folio_number-1
    # pages with an v are on the 'right' side so their page number is 1 higher than their left-handed counterparts
    if 'v' in image_id: folio_number += 1
    return folio_number

# def _get_folio_id_from_url(transcription_collection_id: str, page_number:int) -> str:
#     """
#     Fetches and extracts the folio id from a manuscript viewer page.

#     Given a transcription collection ID and a page number, this function:
#     1. Constructs the folio viewer URL using `manuscript_information`.
#     2. Sends an HTTP GET request to retrieve the page content.
#     3. Applies a regular expression (also from `manuscript_information`) to extract 
#        the folio id from the page's HTML.
#     4. Validates and returns the folio id in the format like '12r' or '7v'.

#     Args:
#         transcription_collection_id (str): The key identifying the manuscript collection.
#         page_number (int): The page number to fetch the folio for.

#     Returns:
#         str: The cleaned folio id (e.g., '45r', '23v').

#     Raises:
#         ValueError: If the HTTP request fails or the folio id cannot be extracted.
#     """

#     folio_url = manuscript_information[transcription_collection_id]['image_link']+str(page_number)
#     response = requests.get(folio_url)
#     if response.status_code != requests.codes.ok:
#         raise ValueError("{} from {}".format(response.status_code, folio_url))
#     import re
    
#     #'\"bindUrl\":\"\",\"url\":\"https://gallica.bnf.fr/services/ajax/mode/SINGLE/ark:/12148/btv1b52515201k/f282/f282.item..SINGLE\",\"etat\":\"\"},\"IsPageVerticalDisplay\":false,\"changed\":true},\"contenu\":\"135v'
    
#     #folio_number_pattern = re.compile(manuscript_information[transcription_collection_id]['folio_number_pattern'])
#     folio_number_pattern_raw = r'\"bindUrl\\":\\"\\",\\"url\\":\\"https:\/\/gallica\.bnf\.fr\/services\/ajax\/mode\/SINGLE\/ark:\/12148\/btv1b52515201k\/f\d{1,3}\/f\d{1,3}\.item\.\.SINGLE\\",\\"etat\\":\\"\\"},\\"IsPageVerticalDisplay\\":false,\\"changed\\":true},\\"contenu\\":\\"\d{1,3}[r|v]'
#     #folio_number_pattern_raw = r'\"bindUrl\\":\\"\\",\\"url\\":\\"https:\/\/gallica\.bnf\.fr\/services\/ajax\/mode\/SINGLE\/ark:\/12148\/btv1b52515201k\/f\d{1,3}\/f\d{1,3}\.item\.\.SINGLE\\",\\"etat\\":\\"\\"},\\"IsPageVerticalDisplay\\":false,\\"changed\\":true},\\"contenu\\":\\"\d{1,3}[r|v]'
#     print(folio_number_pattern_raw)
#     folio_number_pattern = re.compile(folio_number_pattern_raw)
#     folio_numbers = folio_number_pattern.findall(response.text)
#     if len(folio_numbers) == 1: 
#         clean_folio_number_pattern = r'\d{1,3}[r|v]'
#         return clean_folio_number_pattern.findall(folio_numbers[0])[0]
#     else:
#         raise NameError("folio_numbers:", folio_numbers, folio_url)


def _create_folio_id_from_manifest(manifest_url:str) -> dict[str, str]:
    folio_id_url_map = dict()
    response = requests.get(manifest_url)
    manifest_json = response.json()
    for canvas in manifest_json["sequences"][0]["canvases"]:
        folio_id_url_map[canvas["label"]] = canvas["@id"]
    return folio_id_url_map


def _create_folio_id_url_map(collection_id:str, ) -> dict[str, str]:
    manifest_url = manuscript_information[collection_id]['manifest']
    # only create a dict for supported libraries
    if 'gallica' in manifest_url:
        return _create_folio_id_from_manifest(manifest_url)
    else:
        return None
        
def _identify_folio_ids(title_urn:str) -> list[str]:
    """
        #2r4r -> 2r,2v,3r,3v,4r
    """

    title_parts = title_urn.replace("urn:cts:formulae:",'').split('.')
    folio_ids_borders = re.findall(r'\d+[r|v]', title_parts[1])
    
    
    match len(folio_ids_borders):
        case 0:
            raise ValueError("No folio ids found in "+title_urn)
        case 1:
            return folio_ids_borders
        case 2:
            pass
        case _: # > 2
            raise ValueError("Too my folio ids found in "+title_urn)
    lower_border = folio_ids_borders[0]
    upper_border = folio_ids_borders[1]
    folio_ids = [lower_border]
    current_element = lower_border
    while current_element != upper_border:
        if 'r' in current_element:
            current_element = current_element.replace('r', 'v')
        elif 'v' in current_element:
            current_element  = current_element.replace('v', '')
            current_element = str(int(current_element)+1)+'r'
        folio_ids.append(current_element)
    folio_ids.append(upper_border)
    return folio_ids

def _make_images_dict_v2(collection_id:str,  title_urn:str, logger:logging.Logger) -> dict[str:str]:
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
    
    
    
    folio_ids = _identify_folio_ids(title_urn)
    

    folio_id_url_map = _create_folio_id_url_map(collection_id)

    images_dict = dict()


    for folio_id in folio_ids:
        if folio_id_url_map is None:
            print('Automatic extraction of images_dict for {} is not yet supported.'.format(collection_id))
            page_number = _get_page_number(folio_id, collection_id)
            folio_url = manuscript_information[collection_id]['image_link']+str(page_number)
            response = requests.get(folio_url)
            if response.status_code == requests.codes.ok:
                images_dict[folio_id] = folio_url
            else:
                logger.warning("{} from {}".format(response.status_code, folio_url))
                #print("{} from {}".format(response.status_code, folio_url))
                images_dict[folio_id] = folio_url
        else:
            images_dict[folio_id] = folio_id_url_map[folio_id]
    return images_dict



# def _make_images_dict(folio_id_url_map,  title_urn:str, logger:logging.Logger) -> dict[str:str]:
#     """Function that creates a dict, that holds url to the manuscript images.
#     Every URL is checked beforehand and only included if it returns content.

#     Args:
#         title_urn: 
#         logger: 

#     Returns:
#         A dict similar to this:
#         {'images': 
#             {<folio id>: <url to the manuscript image>}
#         }

#     """
    
#     title_parts = title_urn.replace("urn:cts:formulae:",'').split('.')

#     folio_ids = re.findall(r'\d+[r|v]', title_parts[1])
#     if folio_ids == []: raise ValueError("No folio ids found in "+title_urn)

#     images_dict = dict()
#     if folio_id_url_map is None:
#         raise NotImplementedError('Automatic extraction of images_dict for this data is not yet supported.')
#     else:
#         for folio_id in folio_ids:
#             images_dict[folio_id] = folio_id_url_map[folio_id]
#     return images_dict

# def _make_images_dict_deprecated(title_urn:str, logger:logging.Logger) -> dict[str:str]:
#     """Function that creates a dict, that holds url to the manuscript images.
#     Every URL is checked beforehand and only included if it returns content.

#     Args:
#         title_urn: 
#         logger: 

#     Returns:
#         A dict similar to this:
#         {'images': 
#             {<folio id>: <url to the manuscript image>}
#         }

#     """

#     #title_from_xml = re.sub(".+lat \[fol\.", "", title_from_xml)
#     #title_from_xml = re.sub("<span.+", "", title_from_xml)
#     title_parts = title_urn.replace("urn:cts:formulae:",'').split('.')
#     transcription_collection_id = title_parts[0]

#     folio_ids = re.findall(r'\d+[r|v]', title_parts[1])
#     if folio_ids == []: raise ValueError("No folio ids found in "+title_urn)

#     folio_id_mismatches = list[tuple]

#     images_dict = dict()
#     for folio_id in folio_ids:
#         page_number = _get_page_number(folio_id, transcription_collection_id)
#         folio_url = manuscript_information[transcription_collection_id]['url']+"/canvas/f"+str(page_number)
#         response = requests.get(folio_url)
#         if response.status_code == requests.codes.ok:
#             images_dict[folio_id] = folio_url
#         else:
#             logger.debug("{} from {}".format(response.status_code, folio_url))
#             #print("{} from {}".format(response.status_code, folio_url))
#             images_dict[folio_id] = folio_url
#         obtained_folio_number = _get_folio_id_from_url(transcription_collection_id, page_number)
#         if obtained_folio_number != folio_id:
#             folio_id_mismatches.append((folio_id, obtained_folio_number, folio_url))
#     return images_dict, folio_id_mismatches


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
            #folio_id_url_map = _create_folio_id_url_map(collection_id)
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
                                #images_dict = _make_images_dict(folio_id_url_map,  title_urn, logger)
                                images_dict = _make_images_dict_v2(collection_id=collection_id,title_urn=title_urn,logger=logger)
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