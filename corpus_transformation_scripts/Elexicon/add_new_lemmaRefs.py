from glob import glob
from lxml import etree
import sys
import re
from os import environ

home_dir = environ.get('HOME', '')
corpus_folder = sys.argv[1] if len(sys.argv) > 1 else home_dir + '/formulae-corpora/'
scripts_folder = sys.argv[2] if len(sys.argv) > 2 else home_dir + '/scripts/'

latins = [x for x in glob(corpus_folder + 'data/**/*lat*.xml', recursive=True) if 'elexicon' not in x]
germans = [x for x in glob(corpus_folder + 'data/**/*deu*.xml', recursive=True) if 'elexicon' not in x]
elexes = [x for x in glob(corpus_folder + 'data/elexicon/*/*.xml') if '__capitains__' not in x]
lex_xml = etree.parse(scripts_folder + 'corpus_transformation_scripts/Elexicon/Begriffe_eLexikon.xml')

lex_dict = {}
for lem in lex_xml.xpath('/xml/lem'): 
    lex_dict[lem.text.strip()] = lem.get('elex').strip()
first_words = [] 
second_words = [] 
for k, v in lex_dict.items(): 
    words = k.split() 
    if len(words) == 2: 
        first_words.append(words[0]) 
        second_words.append(words[1])
    
ns = {'tei': "http://www.tei-c.org/ns/1.0"}

def set_lemmaRef(orig, lemma, next_lem, prev_lem): 
    if lemma in first_words: 
        if '{} {}'.format(lemma, next_lem) in lex_dict: 
            orig.set('lemmaRef', lex_dict['{} {}'.format(lemma, next_lem)]) 
            return True 
        elif '{} {}'.format(lemma, prev_lem) in lex_dict: 
            orig.set('lemmaRef', lex_dict['{} {}'.format(lemma, prev_lem)]) 
            return True 
    elif lemma in second_words: 
        if '{} {}'.format(prev_lem, lemma) in lex_dict: 
            orig.set('lemmaRef', lex_dict['{} {}'.format(prev_lem, lemma)]) 
            return True 
        elif '{} {}'.format(next_lem, lemma) in lex_dict: 
            orig.set('lemmaRef', lex_dict['{} {}'.format(next_lem, lemma)]) 
            return True 
    return False 

for l in latins: 
    xml = etree.parse(l) 
    words = xml.xpath('//tei:w', namespaces=ns) 
    for i, w_tag in enumerate(words): 
        lemma = w_tag.get('lemma') 
        next_lem = words[i + 1].get('lemma') if len(words) > i + 1 else '' 
        prev_lem = words[i - 1].get('lemma') if i - 1 >= 0 else '' 
        if lemma in lex_dict.keys(): 
            if set_lemmaRef(w_tag, lemma, next_lem, prev_lem) is False: 
                w_tag.set('lemmaRef', lex_dict[lemma]) 
        else: 
            set_lemmaRef(w_tag, lemma, next_lem, prev_lem) 
    xml.write(l, encoding="utf-8", pretty_print=True) 
    
for g in germans: 
    xml = etree.parse(g) 
    latin_words = xml.xpath('//tei:seg[@type="latin-word;"]/tei:w', namespaces=ns) 
    for i, w in enumerate(latin_words): 
        if w.text.lower() in lex_dict.keys(): 
            if set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False: 
                w.set('lemmaRef', lex_dict[w.text.lower()]) 
        elif set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False:
            w.attrib.pop('lemmaRef', None)
    xml.write(g, encoding='utf-8', pretty_print=True) 
    
for elex in elexes: 
    xml = etree.parse(elex) 
    latin_words = xml.xpath('//tei:w[@type="latin-word"]', namespaces=ns) 
    for i, w in enumerate(latin_words): 
        if w.text.lower() in lex_dict.keys(): 
            if set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False: 
                w.set('lemmaRef', lex_dict[w.text.lower()]) 
        elif set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False:
            w.attrib.pop('lemmaRef', None)
    xml.write(elex, encoding='utf-8', pretty_print=True) 
