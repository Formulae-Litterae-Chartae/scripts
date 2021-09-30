import subprocess
from lxml import etree
from glob import glob
import re
from string import punctuation
import os

ns = {'tei': "http://www.tei-c.org/ns/1.0"}
xmls = list()
for corpus in ['andecavensis', 'marculf', 'marmoutier_serfs', 'auvergne']:
    xmls += glob('/home/matt/formulae-corpora/data/{}/**/*.lat00*.xml'.format(corpus), recursive=True)
    xmls += glob('/home/matt/formulae-corpora/data/{}/**/*.deu001.xml'.format(corpus), recursive=True)
lex_xml = etree.parse('/home/matt/scripts/corpus_transformation_scripts/Elexicon/Begriffe_eLexikon.xml')
lex_dict = {}
for lem in lex_xml.xpath('/xml/lem'):
    lex_dict[lem.text.strip()] = lem.get('elex').strip()
del lex_xml
first_words = []
second_words = []
for k, v in lex_dict.items():
    words = k.split()
    if len(words) == 2:
        first_words.append(words[0])
        second_words.append(words[1])


def test_text(lemmas, orig):
    if len(lemmas) != len(orig):
        return '\n{}\n{}'.format(' '.join([n.split('\t')[0] for n in lemmas]).lower(), ' '.join([''.join(x.xpath('.//text()')) for x in orig]).lower())
    not_found = []
    for i, word in enumerate(lemmas):
        inflected, lemma, display_lem = word.split('\t')[:3]
        if not re.search(r'\w', inflected):
            continue
        inflected = re.sub(r'[{}«»„“‚‘’”\[\]]'.format(punctuation), '', inflected)
        prev_lem = '' 
        next_lem = ''
        if i < len(lemmas) - 1:
            try:
                next_lem = lemmas[i+1].split('\t')[1]
            except IndexError:
                print(lemmas[i+1], i)
                continue
        if i > 0:
            prev_lem = lemmas[i-1].split('\t')[1]
        tried = []
        if inflected.lower().replace('v', 'u') != re.sub(r'[{}«»„“‚‘’”\[\]]'.format(punctuation), '', ''.join(orig[i].xpath('.//text()', namespaces=ns)).lower().replace('v', 'u')):
            not_found.append((inflected, tried))
            continue
        #try:
            #while inflected.lower().replace('v', 'u') != re.sub(r'[{}«»„“‚‘’”\[\]]'.format(punctuation), '', ''.join(orig[i].xpath('.//text()', namespaces=ns)).lower().replace('v', 'u')):
                #try:
                    #tried.append(re.sub(r'[{}«»„“‚‘’”\[\]]'.format(punctuation), '', ''.join(orig[i].xpath('.//text()', namespaces=ns)).lower().replace('v', 'u')))
                    #i += 1
                    #if i == len(orig):
                        #not_found.append((inflected, tried))
                        #continue
                #except IndexError:
                    #not_found.append((inflected, tried))
                    #continue
        #except IndexError as E:
            #print(i, inflected, lemma, len(orig), E)
            #continue
        #except AttributeError as E:
            #print(prev_lem, next_lem, inflected, lemma, len(orig), E)
            #continue
        orig[i].set('lemma', lemma.lower())
        orig[i].set('n', display_lem)
        for lem in lemma.split('/'):
            if lem in lex_dict.keys():
                if set_lemmaRef(orig[i], lem, next_lem, prev_lem) is False:
                    orig[i].set('lemmaRef', lex_dict[lem])
            else:
                set_lemmaRef(orig[i], lemma, next_lem, prev_lem)
    return not_found


def set_lemmaRef(orig, lemma, next_lem, prev_lem):
    for lem in lemma.split('/'):
        for n_lem in next_lem.split('/'):
            for p_lem in prev_lem.split('/'):
                if lem in first_words:
                    if '{} {}'.format(lem, n_lem) in lex_dict:
                        orig.set('lemmaRef', lex_dict['{} {}'.format(lem, n_lem)])
                        return True
                    elif '{} {}'.format(lem, p_lem) in lex_dict:
                        orig.set('lemmaRef', lex_dict['{} {}'.format(lem, p_lem)])
                        return True
                elif lem in second_words:
                    if '{} {}'.format(p_lem, lem) in lex_dict:
                        orig.set('lemmaRef', lex_dict['{} {}'.format(p_lem, lem)])
                        return True
                    elif '{} {}'.format(n_lem, lem) in lex_dict:
                        orig.set('lemmaRef', lex_dict['{} {}'.format(n_lem, lem)])
                        return True
    return False


for xml_file in sorted(xmls):
    print(xml_file)
    xml = etree.parse(xml_file).getroot()
    '''new_xml = xml_file.replace('/formulae/', '/test_lemmaRef/')
    try:
        os.makedirs(os.path.dirname(new_xml))
    except OSError:
        pass'''
    form_name = os.path.basename(xml_file)
    if 'lat001' in xml_file:
        lem_file = '/home/matt/lemmatization/pyrrha_output/results/{}.txt'.format(form_name.replace('.xml', ''))
        try:
            with open(lem_file) as f:
                lems = f.read().strip().split('\n')
        except FileNotFoundError:
            print(xml_file, lem_file)
            continue
        not_found = test_text(lems, xml.xpath('//tei:w[not(@type="no-search")]', namespaces=ns))
        if not_found:
            print(xml_file, not_found)
        elif xml.xpath('//tei:w[not(@lemma) and not(@type="no-search")]', namespaces=ns):
            print(xml_file, '\n\t', '; '.join(x.text for x in xml.xpath('//tei:w[not(@lemma)]', namespaces=ns)))
        else:
            xml.getroottree().write(xml_file)
            #subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(xml_file), '/home/matt/docx_tei_cte_conversion/ElasticSearch/extract_text_search_to_xml.xsl', '-o:/home/matt/results/formulae/search/{}'.format(xml_file.split('/')[-1].replace('xml', 'txt'))])
    else:
        latin_words = xml.xpath('//tei:seg[@type="latin-word;"]/tei:w', namespaces=ns)
        for i, w in enumerate(latin_words):
            if w.text.lower() in lex_dict.keys():
                if set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False:
                    w.set('lemmaRef', lex_dict[w.text.lower()])
            else:
                set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ')
        xml.getroottree().write(xml_file)

# TO RECREATE THE TEXT FILES USED TO POPULATE THE ELASTICSEARCH INDEX

"""for xml_file in xmls:
     subprocess.run(['java', '-jar',  '/home/matt/Downloads/SaxonHE9-8-0-11J/saxon9he.jar', '{}'.format(xml_file), '/home/matt/docx_tei_cte_conversion/extract_text_search.xsl', '-o:/home/matt/results/formulae/search/{}'.format(xml_file.split('/')[-1].replace('xml', 'txt'))])"""
