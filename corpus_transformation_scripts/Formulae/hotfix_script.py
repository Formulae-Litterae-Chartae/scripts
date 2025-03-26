from glob import glob
import re
from os import makedirs, environ, getcwd, remove, rename
import os.path
from lxml import etree
from collections import defaultdict
import logging
import argparse
from tqdm import tqdm
from util import subprocess_run, get_logger
from bs4 import BeautifulSoup

parser=argparse.ArgumentParser(
    description="Script to hotfix things in the corpora. These fixes should be only temporarily until the next big update of the documents.")
parser.add_argument("folder", type=str,default='andecavensis')
parser.add_argument("old_text", type=str,default='<seg type="italic;">P</seg><seg type="italic;subscript;smaller-text;">16a</seg>', 
                    help='the string to be replaced')
parser.add_argument("new_text", type=str, default='<seg type="italic;">P</seg><seg type="italic;subscript;smaller-text;">16b</seg>', 
                    help='the string that will replace it')

parser.add_argument('file_type',
                    default='all',
                    const='all',
                    nargs='?',
                    choices=['latin', 'german', 'capitains' 'all'],
                    help='To which file should the hotfix apply? (default: %(default)s)')
args=parser.parse_args()
logger = get_logger()

def apply_hotfix(folder:str, old_text, new_text, logger:logging.Logger):

    subfolders = [ f.path for f in os.scandir(os.path.join(folder)) if f.is_dir() ]
    for subfolder in subfolders:
        if os.path.isfile(subfolder):
            import xml.etree.ElementTree as ET
            tree = ET.parse('subfolder')
            root = tree.getroot()
            for element in root.findall('seg'):
                element.text = element.text.replace(old=old_text, new=new_text)

    rank = country.find('rank').text

    name = country.get('name')

    print(name, rank)
