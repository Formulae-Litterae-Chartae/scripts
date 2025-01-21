import logging
import argparse
import os
from bs4 import BeautifulSoup

def check_existence_notes(logging, file_or_folder_path:str, notes_threshold=25): 
    # Example note: <note type="n1" place="foot" n="2"><p xml:space="preserve"> Schon <bibl n="&lt;span class=&#34;surname&#34;&gt;Zeumer&lt;/span&gt;, Karl: Formulae Merowingici et Karolini aevi, Hannover 1886.">K. Zeumer, Formulae</bibl>, S. 28, vermutet, dass es sich bei <seg type="italic;">nascuntur</seg>, um einen Schreibfehler für <seg type="italic;">noscuntur</seg> handelt, was sich aufgrund des Textverlustes nicht mehr sicher rekonstruieren lässt.</p></note>
    if os.path.isdir(file_or_folder_path):
        # filter all files in folder with "lat" in it
        file_paths=[]
        for path, subdirs, files in os.walk(file_or_folder_path):
            for file in files:
                if 'lat' in file:
                    file_paths.append(os.path.join(path, file))
    else:
        file_paths=[file_or_folder_path]
    threshold_not_undercut = True
    for file_path in file_paths:
        with open(file_path) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            notes = soup.find_all('note')
            if notes_threshold > len(notes):
                logging.warning('Low number of notes ({}), which indicates a error from transform_cte_to_dll.py for {}'.format(len(notes),file_path))
                threshold_not_undercut = False
    return threshold_not_undercut

def compare_notes(logging, xml_from_cte:str, xml_after_conversion:str):
    """
    compares the number of notes (<note place="foot" type="a1" rend="visible bracket" targetEnd="#w11"><mentioned rend="visible bracket"><hi rend="font-size:10pt;">nascuntur] </hi></mentioned><hi rend="font-size:10pt;font-style:italic;">Zeu schlägt vor </hi><hi rend="font-size:10pt;">noscuntur </hi><hi rend="font-size:10pt;font-style:italic;">zu emendieren („</hi><hi rend="font-size:10pt;">noscuntur</hi><hi rend="font-size:10pt;font-style:italic;">, fortasse corrigendum“) </hi></note>)
    """

    with open(xml_from_cte) as fp:
        xml_from_cte_soup = BeautifulSoup(fp, 'html.parser')
        xml_from_cte_notes = xml_from_cte_soup.find_all('note')
    with open(xml_after_conversion) as fp:
        xml_after_conversion_soup = BeautifulSoup(fp, 'html.parser')
        xml_after_conversion_notes = xml_after_conversion_soup.find_all('note')
    if len(xml_from_cte_notes) != len(xml_after_conversion_notes):
        logging.error("Not all notes transferred! {} in {} and {} in {}".format(len(xml_from_cte_notes),
                                                                                xml_from_cte,
                                                                                len(xml_after_conversion_notes),
                                                                                xml_after_conversion))
        for from_cte, xml_after in zip(xml_from_cte_notes, xml_after_conversion_notes):
            print(from_cte)
            print(xml_after)
            print('---')


def run_checks(logging, file_path):
    check_existence_notes(logging, file_path)
    xml_from_cte = "/home/thorben.schomacker/git/scripts/formel_transform/output/auvergne/Latin/Auvergne 1.xml"
    xml_after_conversion = "/home/thorben.schomacker/git/formulae-corpora/data/auvergne/form002/auvergne.form002.lat001.xml"
    compare_notes(logging, xml_from_cte, xml_after_conversion)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                    encoding='utf-8', 
                    datefmt='%H:%M:%S')
    logging.getLogger().setLevel('INFO')
    file_path = "/home/thorben.schomacker/git/formulae-corpora/data/auvergne"
    run_checks(logging, file_path)