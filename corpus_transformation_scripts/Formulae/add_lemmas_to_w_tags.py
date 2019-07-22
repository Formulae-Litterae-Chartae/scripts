import subprocess
from lxml import etree
from glob import glob
import re
from string import punctuation
import os

ns = {'tei': "http://www.tei-c.org/ns/1.0"}
xmls = glob('/home/matt/results/formulae/data/andecavensis/*/*lat001.xml')
xmls += glob('/home/matt/results/formulae/data/andecavensis/*/*deu001.xml')
lex_xml = etree.parse('/home/matt/docx_tei_cte_conversion/elexicon/Begriffe_eLexikon.xml')
lex_dict = {}
for lem in lex_xml.xpath('/xml/lem'):
    lex_dict[lem.text] = lem.get('elex')
del lex_xml
first_words = []
second_words = []
for k, v in lex_dict.items():
    words = k.split()
    if len(words) == 2:
        first_words.append(words[0])
        second_words.append(words[1])


def test_text(lemmas, orig):
    not_found = []
    for i, word in enumerate(lemmas):
        prev_lem = '' 
        next_lem = ''
        if i < len(lemmas) - 1:
            next_lem = lemmas[i+1].split(';')[1]
        if i > 0:
            prev_lem = lemmas[i-1].split(';')[1]
        inflected, lemma = word.split(';')[:2]
        tried = []
        try:
            while inflected.replace('v', 'u') != re.sub(r'[{}„“‚‘’”]'.format(punctuation), '', orig[i].text.lower().replace('v', 'u')):
                try:
                    tried.append(re.sub(r'[{}„“‚‘’”]'.format(punctuation), '', orig[i].text.lower().replace('v', 'u')))
                    i += 1
                    if i == len(orig):
                        not_found.append((inflected, tried))
                        continue
                except IndexError:
                    not_found.append((inflected, tried))
                    continue
        except IndexError:
            print(i, inflected, lemma, len(orig))
            continue
        orig[i].set('lemma', lemma)
        set_lemmaRef(orig[i], lemma, next_lem, prev_lem)
    return not_found


def set_lemmaRef(orig, lemma, next_lem, prev_lem):
    if lemma in first_words:
        if '{} {}'.format(lemma, next_lem) in lex_dict:
            orig.set('lemmaRef', lex_dict['{} {}'.format(lemma, next_lem)])
        elif '{} {}'.format(lemma, prev_lem) in lex_dict:
            orig.set('lemmaRef', lex_dict['{} {}'.format(lemma, prev_lem)])
    elif lemma in second_words:
        if '{} {}'.format(prev_lem, lemma) in lex_dict:
            orig.set('lemmaRef', lex_dict['{} {}'.format(prev_lem, lemma)])
        elif '{} {}'.format(next_lem, lemma) in lex_dict:
            orig.set('lemmaRef', lex_dict['{} {}'.format(next_lem, lemma)])


for xml_file in xmls:
    print(xml_file)
    xml = etree.parse(xml_file).getroot()
    '''new_xml = xml_file.replace('/formulae/', '/test_lemmaRef/')
    try:
        os.makedirs(os.path.dirname(new_xml))
    except OSError:
        pass'''
    number = xml_file.split('.')[-3].replace('form', '').lstrip('0')
    if 'lat001' in xml_file:
        lem_file = '/home/matt/results/angers_lemmatisiert_neu/Form._And._{}_tokenized_bi_lemmed.csv'.format(number)
        try:
            with open(lem_file) as f:
                lems = f.read().split('\n')[1:-1]
        except FileNotFoundError:
            continue
        not_found = test_text(lems, xml.xpath('//tei:w', namespaces=ns))
        if not_found:
            print(xml_file, not_found)
        else:
            xml.getroottree().write(xml_file)
            subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(xml_file), '/home/matt/docx_tei_cte_conversion/extract_text_search.xsl', '-o:/home/matt/results/formulae/search/{}'.format(xml_file.split('/')[-1].replace('xml', 'txt'))])
    else:
        latin_words = xml.xpath('//tei:seg[@type="latin-word;"]/tei:w', namespaces=ns)
        for i, w in enumerate(latin_words):
            set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ')
        xml.getroottree().write(xml_file)

# TO RECREATE THE TEXT FILES USED TO POPULATE THE ELASTICSEARCH INDEX

"""for xml_file in xmls:
     subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(xml_file), '/home/matt/docx_tei_cte_conversion/extract_text_search.xsl', '-o:/home/matt/results/formulae/search/{}'.format(xml_file.split('/')[-1].replace('xml', 'txt'))])"""
