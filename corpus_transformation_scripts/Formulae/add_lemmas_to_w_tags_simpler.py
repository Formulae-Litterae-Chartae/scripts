import subprocess
from lxml import etree
from glob import glob
import re
from string import punctuation
import os
import logging
import argparse

default_home_dir = os.environ.get('HOME', '')

parser=argparse.ArgumentParser(description="Script to add lemma annotation to w-tags in the tei xml documents.")
parser.add_argument("home_dir", type=str,default=default_home_dir, help="Directory, where both 'formulae-corpora' and 'scripts' are stored")
default_lemmatized_corpora = ['andecavensis', 'auvergne', 'bourges', 'flavigny', 'formulae_marculfinae', 'marculf', 'marmoutier_dunois', 
                                'marmoutier_serfs', 'marmoutier_vendomois', 'marmoutier_vendomois_appendix', 'pancarte_noire', 'telma_cormery', 
                                'telma_marmoutier', 'telma_martin_tours', 'tours', 'tours_ueberarbeitung']
parser.add_argument('lemmatized_corpora', nargs='*', default=default_lemmatized_corpora, help="Optional argument to limit the corpora to a given list. If empty the default is used.")
args=parser.parse_args()

log_file_path=os.path.join(args.home_dir,'scripts/results/add_lemmas_to_w_tags_simpler.log')
# create the log_file
with open(log_file_path, 'w'): pass

logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                    encoding='utf-8', 
                    datefmt='%H:%M:%S',
                    filename=log_file_path)
logging.getLogger().setLevel('INFO')



ns = {'tei': "http://www.tei-c.org/ns/1.0"}
home_dir = args.home_dir
xmls = list()
lemmatized_corpora = args.lemmatized_corpora
for corpus in lemmatized_corpora: #
    xmls += glob(home_dir + '/formulae-corpora/data/{}/**/*.lat00*.xml'.format(corpus), recursive=True)
    xmls += glob(home_dir + '/formulae-corpora/data/{}/**/*.deu001.xml'.format(corpus), recursive=True)
lex_xml = etree.parse(home_dir + '/scripts/corpus_transformation_scripts/Elexicon/Begriffe_eLexikon.xml')
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

def _export_lemma_comparison(lemmas_inflected,orig_inflected,xml_file):
    import csv
    csv_file_name=xml_file.split('/')[-1].replace('xml', 'tsv')
    csv_file_path = os.path.abspath(csv_file_name)
    with open(csv_file_path, 'w+') as csvfile:
        tsv_writer = csv.writer(csvfile, delimiter='\t')
        tsv_writer.writerow(['lemmas_inflected',  'orig_inflected'])
        for i, _ in enumerate(lemmas_inflected): 
            if i < len(orig_inflected):
                tsv_writer.writerow([lemmas_inflected[i],  orig_inflected[i]])
            else:
                tsv_writer.writerow([lemmas_inflected[i], ''])
    print('written to '+str(csv_file_path))
        
def clean_string(input_str:str) -> str:
    """
    removes all punctuation and trailing spaces
    """
    extended_punctuation = r'[{}«»„“‚‘’”\[\]…|]'.format(punctuation)
    punctuation_removed = re.sub(extended_punctuation, '', input_str)
    all_lower_case = punctuation_removed.lower()
    unified_v_u = all_lower_case.replace('v', 'u')
    #.strip()
    if "" == unified_v_u: logging.error('"{}" is not a valid string and should have been removed from the list in previous steps.'.format(input_str))
    return unified_v_u

def test_text(lemmas: list, orig: list, xml_file=None) -> list | str:
    """
    Compares lemmas and orig. Resulting in three scenarios:
        1) If it returns an empty list                  -> OK
        2) If it returns a list with one or more items  -> ERROR
        3) If it returns a string                       -> ERROR
    """
    if len(lemmas) != len(orig):
        logging.info('Length mismatch: There are {} lemmas and {} originals. But these lists should match in size. Trying to resolve this issue.'.format(len(lemmas), len(orig)))
        orig_inflected = [''.join(x.xpath('.//text()')) for x in orig]
        lemmas_inflected = [n.split('\t')[0] for n in lemmas]
        lemmas_text = list()
        orig_text = list()
        # | indicate a page break. They are quasi punctuation and should not be lemmatized. This can solve some conflicts.
        # obtaining the indices is only used for logging purposes
        pipe_indices = [i for i, orig_word in enumerate(orig_inflected) if orig_word == "|"]
        if pipe_indices:
            orig_inflected = [element for element in orig_inflected if element != '|']
            if len(lemmas_inflected) == len(orig_inflected):
                logging.info('Resolved: Length mismatch removed all "|" that where found in orig_text at indices: {}'.format(pipe_indices))
            else: 
                logging.warning('Length mismatch continues after having removed all "|" that where found in orig_text at indices: {} but there are still {} lemmas_inflected and {} originals'.format(pipe_indices, len(lemmas_inflected), len(orig_inflected)))
        for i, w in enumerate(lemmas_inflected):
            if i >= len(orig_inflected):
                logging.warning('Index i: {} exceeded length of orig_inflected: {}. Therefore no lemmatization is done. After every "!!!" is one error in the following output:'.format(i, len(orig_inflected)))
                return '\n{}\n{}'.format(' '.join(lemmas_text + ['!!!'] + [n.split('\t')[0] for n in lemmas[i:]]).lower(), ' '.join(orig_text + ['!!!']))
            else:
                clean_orig_inflected_element = clean_string(orig_inflected[i])
                clean_lemmas_inflected_w_element = clean_string(w)
                if clean_lemmas_inflected_w_element == clean_orig_inflected_element :
                    lemmas_text.append(w.lower().replace('v', 'u'))
                    orig_text.append(w.lower().replace('v', 'u'))
                else:
                    logging.warning('There was mismatch at list index {} (w={} \t orig={}). Therefore no lemmatization is done. After every "!!!" is one error in the following output:'.format(i, clean_lemmas_inflected_w_element, clean_orig_inflected_element))
                    logging.warning('orig_inflected={}'.format(orig_inflected))
                    _export_lemma_comparison(lemmas_inflected,orig_inflected,xml_file)
                    return '\n{}\n{}'.format(' '.join(lemmas_text + ['!!!'] + [n.split('\t')[0] for n in lemmas[i:]]).lower(), ' '.join(orig_text + ['!!!'] + [''.join(x.xpath('.//text()')) for x in orig[i:]]).lower())
        orig=orig_inflected
    not_found = []
    for i, word in enumerate(lemmas):
        inflected, lemma, display_lem = word.split('\t')[:3]
        if not re.search(r'\w', inflected):
            continue
        #inflected = re.sub(r'[{}«»„“‚‘’”\[\]…|]'.format(punctuation), '', inflected).strip()
        inflected = clean_string(inflected)
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
        # left side -> pyrrha ; right side -> word from xml file
        if inflected.lower().replace('v', 'u') != re.sub(r'[{}«»„“‚‘’”\[\]…|]'.format(punctuation), '', ''.join(orig[i].xpath('.//text()', namespaces=ns)).lower().replace('v', 'u')):
        # I am not sure, why the xml_strings are obtained a second time. Maybe because of the namespace attribute
        # Anyhow the | need to be removed again
        #word_from_xml = clean_string(orig[i])
        #if inflected != word_from_xml:
            not_found.append((inflected, i, word_from_xml))
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

logging.info('Parse '+str(len(xmls))+' xml files from '+str(lemmatized_corpora))
for xml_file in sorted(xmls):
    #print(xml_file)
    
    xml = etree.parse(xml_file).getroot()
    '''new_xml = xml_file.replace('/formulae/', '/test_lemmaRef/')
    try:
        os.makedirs(os.path.dirname(new_xml))
    except OSError:
        pass'''
    form_name = os.path.basename(xml_file)
    if 'lat001' in xml_file:
        lem_file = home_dir + '/Lemmatization/pyrrha_output/results/{}.txt'.format(form_name.replace('.xml', ''))
        try:
            with open(lem_file) as f:
                lems = f.read().strip().split('\n')
                logging.info(lem_file)
        except FileNotFoundError:
            logging.error('FileNotFoundError'+'\t'+xml_file+'\t'+lem_file)
            continue
        not_found = test_text(lems, xml.xpath('//tei:w[not(@type="no-search" or normalize-space(text())="|")]', namespaces=ns), xml_file)
        
        if not_found:
            logging.warning('not_found is not empty for '+xml_file)
            if list == type(not_found):
                logging.warning('not_found has '+str(len(not_found))+' items for '+xml_file)
            logging.warning('not_found: '+str(not_found))
        else:
            logging.info('Not found is empty. This indicates a successful lematization process.')
            # if xml.xpath('//tei:w[@lemma and normalize-space(text())="|")]', namespaces=ns):
            #     logging.error('| got a lemma in'+xml_file)
            if xml.xpath('//tei:w[not(@lemma) and not(@type="no-search")]', namespaces=ns):
                #print(xml_file)
                logging.error(xml_file+ " has 'w'-node(s) that are neither no-search nor have lemma. This indicates an incomplete lemmatization process:\n\t" +
                '; '.join(x.text for x in xml.xpath('//tei:w[not(@lemma)]', namespaces=ns)))
            else:
                xml.getroottree().write(xml_file, encoding='utf-8')
                print('written to '+xml_file)
    else:
        latin_words = xml.xpath('//tei:seg[@type="latin-word;"]/tei:w', namespaces=ns)
        for i, w in enumerate(latin_words):
            if w.text.lower() in lex_dict.keys():
                if set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False:
                    w.set('lemmaRef', lex_dict[w.text.lower()])
            else:
                set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ')
        xml.getroottree().write(xml_file, encoding='utf-8')

print('Done! Please the logs for more information:'+str(log_file_path))