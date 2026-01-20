import subprocess
from lxml import etree
from glob import glob
import re
from string import punctuation
import os
import logging
import argparse

def _export_lemma_comparison(lemmas_inflected, orig_inflected, xml_file):
    import csv
    csv_file_name = xml_file.split('/')[-1].replace('xml', 'tsv')
    csv_file_path = os.path.abspath(csv_file_name)

    max_len = max(len(lemmas_inflected), len(orig_inflected))

    with open(csv_file_path, 'w+', newline='') as csvfile:
        tsv_writer = csv.writer(csvfile, delimiter='\t')
        tsv_writer.writerow(['lemmas_inflected', 'orig_inflected'])

        for i in range(max_len):
            lemma_val = lemmas_inflected[i] if i < len(lemmas_inflected) else ''
            orig_val  = orig_inflected[i]  if i < len(orig_inflected)  else ''
            tsv_writer.writerow([lemma_val, orig_val])

    print('written to ' + str(csv_file_path))
    logging.info('Please check to see the errors: ' + str(csv_file_path))
        
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

def test_text(lemmas: list, orig: list[etree._Element], xml_file=None) -> list | str:
    """
    Compares lemmas and orig. Resulting in three scenarios:
        1) If it returns an empty list                  -> OK
        2) If it returns a list with one or more items  -> ERROR
        3) If it returns a string                       -> ERROR
    """
    if not type(orig) == type(list()):
        raise ValueError
    else:
        for w_element in orig:
            if not type(w_element) == etree._Element:
                raise ValueError(str(w_element)+' has type: '+str(type(w_element))+' but should have been: '+ str(etree._Element))
    orig_inflected = [''.join(x.xpath('.//text()')) for x in orig]
    lemmas_inflected = [n.split('\t')[0] for n in lemmas]

    # Never overwrite `orig` (elements). Instead, compute a safe alignment length.
    min_len = min(len(lemmas), len(orig))
    
    if len(lemmas) != len(orig):
        logger.warning(
            "Length mismatch: %s lemmas vs %s lemmas inflected vs %s originals. Proceeding with min_len=%s.",
            len(lemmas), len(lemmas_inflected), len(orig), min_len
        )
    else:
        logger.debug("Length match: %s", len(orig))
    lemmas_text = list()
    orig_text = list()
    for i, w in enumerate(lemmas_inflected):
        if i >= len(orig_inflected):
            logger.warning('Index i: {} exceeded length of orig_inflected: {}. Therefore no lemmatization is done. After every "!!!" is one error in the following output:'.format(i, len(orig_inflected)))
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

    


    # A list collecting all tokens (with their index) from the `lemmas` input  that could not be matched to the corresponding word in the `orig` XML list.
    not_found = []

        # If there are extra lemmas without corresponding <w>, record/report them
    if len(lemmas) > len(orig):
        for j in range(len(orig), len(lemmas)):
            inflected = lemmas[j].split('\t')[0]
            if re.search(r'\w', inflected):
                not_found.append((clean_string(inflected), j))
    
    # If there are extra <w> without corresponding lemmas, record/report them
    if len(orig) > len(lemmas):
        for j in range(len(lemmas), len(orig)):
            # record the surface form of the remaining <w> elements
            extra_w_text = clean_string(''.join(orig[j].xpath('.//text()', namespaces=ns)))
            if re.search(r'\w', extra_w_text):
                not_found.append((extra_w_text, j))

    for i in range(min_len):
        word = lemmas[i]
        inflected, lemma, display_lem = word.split('\t')[:3]

        if not re.search(r'\w', inflected):
            continue

        inflected_clean = clean_string(inflected)

        # Use element list for xpath and attribute setting
        w_el = orig[i]
        w_text_clean = clean_string(''.join(w_el.xpath('.//text()', namespaces=ns)))

        if inflected_clean != w_text_clean:
            not_found.append((inflected_clean, i))
            continue

        w_el.set('lemma', lemma.lower())
        w_el.set('n', display_lem)

        prev_lem = lemmas[i-1].split('\t')[1] if i > 0 else ''
        next_lem = lemmas[i+1].split('\t')[1] if i < min_len - 1 else ''

        for lem in lemma.split('/'):
            if lem in lex_dict:
                if set_lemmaRef(w_el, lem, next_lem, prev_lem) is False:
                    w_el.set('lemmaRef', lex_dict[lem])
            else:
                set_lemmaRef(w_el, lemma, next_lem, prev_lem)

    # If there are extra lemmas without corresponding <w>, record/report them
    if len(lemmas) > len(orig):
        for j in range(len(orig), len(lemmas)):
            inflected = lemmas[j].split('\t')[0]
            if re.search(r'\w', inflected):
                not_found.append((clean_string(inflected), j))

    # If there are extra <w> without lemmas, record/report them too (optional)
    # for j in range(len(lemmas), len(orig)):
    #     not_found.append((clean_string(orig_inflected[j]), j))

    if not_found:
        _export_lemma_comparison(lemmas_inflected, orig_inflected, xml_file)

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

if __name__ == '__main__':
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
    logger = logging.getLogger()
    logger.setLevel('DEBUG')


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



    logger.info('Parse '+str(len(xmls))+' xml files from '+str(lemmatized_corpora))
    success_count = 0 # increased for each successful lemmatization. Used for logging.
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
            w_elements_in_document = xml.xpath('//tei:w[not(@type="no-search" or normalize-space(text())="|")]', namespaces=ns)

            not_found = test_text(lems, orig=w_elements_in_document, xml_file=xml_file)
            
            if not_found:
                if list == type(not_found):
                    logging.warning('not_found is not empty. It has '+str(len(not_found))+' items for '+xml_file)
                logging.warning('not_found: '+str(not_found))
            else:
                logging.debug('Not found is empty. This is a sign of a well-working lematization process.')
                # w-nodes, that should have been lemmatized but were not
                unlemmatized_w = xml.xpath('//tei:w[not(@lemma) and not(@type="no-search")]', namespaces=ns)
                unlemmatized_w_texts = [x.text for x in unlemmatized_w]

                if 0 < len(unlemmatized_w_texts):
                    unlemmatized_w_texts_without_pipes = [w for w in unlemmatized_w_texts if w != '|']
                    if 0 == len(unlemmatized_w_texts_without_pipes):
                        logging.error(" {} has {} '<w>|</w>'-node(s) without type='no-search'. This indicates a failed lemmatization process:\n {}".format(
                            xml_file, len(unlemmatized_w_texts), ";".join(str(x) for x in unlemmatized_w_texts)))
                        logging.error('Consider manually replacing all <w>|</w> with <w type="no-search">|</w> as a hotfix.')
                    else:
                        logging.error(" {} has {} 'w'-node(s) that are neither no-search nor have a lemma. This indicates a failed lemmatization process:\n\t{}".format(xml_file, len(unlemmatized_w), '; '.join(x for x in unlemmatized_w_texts)))
                else:
                    logging.debug('All w-nodes where successfully lemmatized.')
                    xml.getroottree().write(xml_file, encoding='utf-8')
                    #print('written to '+xml_file)
                    logging.info('written to '+xml_file)
                    success_count += 1 
        else:
            latin_words = xml.xpath('//tei:seg[@type="latin-word;"]/tei:w', namespaces=ns)
            for i, w in enumerate(latin_words):
                if w.text.lower() in lex_dict.keys():
                    if set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ') is False:
                        w.set('lemmaRef', lex_dict[w.text.lower()])
                else:
                    set_lemmaRef(w, w.text.lower(), latin_words[i + 1].text.lower() if len(latin_words) > i + 1 else ' ', latin_words[i - 1].text.lower() if i > 0 else ' ')
            xml.getroottree().write(xml_file, encoding='utf-8')

    total_latin_documents = len( [ xml_file for xml_file in xmls if 'lat001' in xml_file])
    print('Done! '+ str(success_count) + '/' +str(total_latin_documents)+' where lemmatized. See the log for more information:'+str(log_file_path))