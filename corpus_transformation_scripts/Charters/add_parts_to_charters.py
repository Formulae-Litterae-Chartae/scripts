from json import load, JSONDecodeError, dump
from lxml import etree
from sys import argv
from string import punctuation
import re

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
punc = punctuation.replace(']', '')
not_typed = []

# The JSON file should be an array (Python list) of objects (Python dicts) with one key called "file" with the name 
# of the XML file to be parsed and changed as a string. The other keys should be the names of the formulaic elements
# that should be encoded with the values being arrays (lists) of strings that represent the different sequential parts
# of each formulaic element. So if a single element is interrupted by one or more other elements, each of the different
# parts of this interrupted element should be its own string in this array.
try:
    with open(argv[1]) as f:
        charter_forms = load(f)
except FileNotFoundError as E:
    print(argv[1], 'is not a file.')
    raise E
except JSONDecodeError as E:
    print(argv[1], 'is not a valid JSON file.')
    raise E


def check_phrases(form_type, words, form_words):                                       
    for i, w in enumerate(words):                                                    
        test_words = words[i:min(len(words) - 1, i + len(form_words))]
        if [x.text for x in test_words] == form_words:
            [x.set('type', re.sub(r'\W+', '-', form_type)) for x in test_words]
            return
        
for charter in charter_forms:
    xml_file = '/home/matt/results/formulae/data/' + charter['file'] + '.xml'
    xml = etree.parse(xml_file)
    xml_words = xml.xpath('//tei:w', namespaces=ns)                   
    for k, v in charter.items():                      
        if k != 'file':                                                        
            for phrase in v:
                form_words = [x.rstrip(punc) for x in phrase.strip().split()]
                check_phrases(k, xml_words, form_words)
    w_no_type = []
    phrase = []
    prev_i = 0
    for i, w in enumerate(xml_words):
        if w.get('type') is None:
            if i == prev_i + 1:
                phrase.append(w.text)
            else:
                if phrase:
                    w_no_type.append(phrase)
                phrase = [w.text]
            prev_i = i
    not_typed.append({charter['file']:[' '.join(p) for p in w_no_type]})
    # taking this line out for now since I am only testing. It should be added back in later.
    # xml.write(xml_file, encoding='utf-8', pretty_print=True)
    
with open(argv[2], mode='w') as f:
    dump(not_typed, f, ensure_ascii=False, indent='\t')
