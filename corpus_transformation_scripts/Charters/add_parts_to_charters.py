from json import load, JSONDecodeError, dump
from lxml import etree
from lxml.builder import ElementMaker
from sys import argv
from string import punctuation
import re
import os

ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
punc = punctuation.replace(']', '')
not_typed = []
typed = {}
json_file = argv[1] # The JSON file with the formulaic parts of the charters
corpus_dir = argv[2] # The /data directory in which the XML files for the corpora are kept
dest_file = argv[3] # The JSON file that will contain the parts of the charters that were not assigned a formulaic category

if not os.path.isdir(corpus_dir):
    raise NotADirectoryError(corpus_dir + ' is not a directory.')

# The JSON file should be an array (Python list) of objects (Python dicts) with one key called "file" with the name 
# of the XML file to be parsed and changed as a string. The other keys should be the names of the formulaic elements
# that should be encoded with the values being arrays (lists) of strings that represent the different sequential parts
# of each formulaic element. So if a single element is interrupted by one or more other elements, each of the different
# parts of this interrupted element should be its own string in this array.
try:
    with open(json_file) as f:
        charter_forms = load(f)
except FileNotFoundError as E:
    print(json_file, 'is not a file.')
    raise E 
except JSONDecodeError as E:
    print(json_file, 'is not a valid JSON file.')
    raise E

E = ElementMaker(namespace='http://www.tei-c.org/ns/1.0', nsmap={None: 'http://www.tei-c.org/ns/1.0'})

def check_phrases(form_type, words, form_words):  
    new_type = re.sub(r'\W+', '-', form_type)
    for i, w in enumerate(words):                                                    
        test_words = words[i:min(len(words), i + len(form_words))]
        if [x.text for x in test_words] == form_words:
            test_words[0].addprevious(E.seg({'function': new_type + '-begin'}))
            test_words[-1].addnext(E.seg({'function': new_type + '-end'}))
            if test_words[0].getparent() != test_words[-1].getparent():
                test_words[0].getparent().append(E.seg({'function': new_type + '-end'}))
                test_words[-1].getparent().insert(0, E.seg({'function': new_type + '-begin'}))
            return
        
for charter in charter_forms:
    xml_file = os.path.join(corpus_dir, charter['file'] + '.xml')
    if not os.path.isfile(xml_file):
        print(xml_file + ' not found.')
        continue
    xml = etree.parse(xml_file)
    xml_words = xml.xpath('//tei:w', namespaces=ns)
    # remove existing seg[@function] elements
    for seg_f in xml.xpath('//tei:seg[@function]', namespaces=ns):
        parent = seg_f.getparent()
        seg_index = parent.index(seg_f)
        for c in seg_f:
            parent.insert(seg_index, c)
            seg_index += 1
        parent.remove(seg_f)
    for k, v in charter.items():                      
        if k != 'file':                                                        
            for phrase in v:
                form_words = [x.rstrip(punc) for x in phrase.strip().split()]
                try:
                    check_phrases(k, xml_words, form_words)
                except:
                    print(charter[k], charter['file'])
    # taking this line out for now since I am only testing. It should be added back in later.
    xml.write(xml_file, encoding='utf-8', pretty_print=True)
    with open(xml_file) as f:
        s = f.read()
    s = re.sub(r'\s*<seg function="([\w\-]+)\-begin"/>', r' <seg function="\1">', s)
    s = re.sub(r'<seg function="([\w\-]+)\-end"/>\s*', r'</seg> ', s)
    with open(xml_file, mode="w") as f:
        f.write(s)
    xml = etree.parse(xml_file)
    xml_words = xml.xpath('//tei:w', namespaces=ns)
    types = {}
    w_no_type = []
    phrase = []
    prev_i = 0
    for i, w in enumerate(xml_words):
        parent = w.getparent()
        if parent.get('function') is None:
            if i == prev_i + 1:
                phrase.append(w.text)
            else:
                if phrase:
                    w_no_type.append(phrase)
                phrase = [w.text]
            prev_i = i
    if phrase and phrase not in w_no_type:
        w_no_type.append(phrase)
    not_typed.append({charter['file']:[' '.join(p) for p in w_no_type]})
    for seg in xml.xpath('//tei:seg[@function]', namespaces=ns):
        if seg.get('function') in types:
            types[seg.get('function')].append(re.sub(r'\s+', ' ', ''.join([t for t in seg.xpath('.//text()')])))
        else:
            types[seg.get('function')] = [re.sub(r'\s+', ' ', ''.join([t for t in seg.xpath('.//text()')]))]
    typed[charter['file']] = types
    
    
with open(dest_file, mode='w') as f:
    dump(not_typed, f, ensure_ascii=False, indent='\t')
    
with open(os.path.splitext(dest_file)[0] + '.csv', mode='w') as f:
    for r in not_typed:
        for k, v in r.items():
            f.write(k + '\n\t')
            f.write('\n\t'.join(v))
            f.write('\n')
            
with open(os.path.splitext(dest_file)[0] + '_types' + '.csv', mode='w') as f:
    for r in typed.keys():
        f.write(r + '\n\t')
        for k, v in typed[r].items():
            f.write(k + '\t')
            f.write('\n\t\t'.join(v))
            f.write('\n\t')
        f.write('\n')
