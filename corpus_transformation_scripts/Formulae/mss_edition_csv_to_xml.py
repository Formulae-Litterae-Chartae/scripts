
import re
from sys import argv
from lxml.builder import E
from lxml import etree
import os
import logging
from util import get_logger
import errno

def xslsx_to_csv(input_path,logger=None) -> str:
    """
    Convert a xslsx-file located at input_path and convert it to csv-file at input_path.
    """
    input_file = find_csv(input_path, file_ending='*.xlsx')
    import pandas as pd 
    df = pd.DataFrame(pd.read_excel(input_file))
    output_file = input_file.replace('xlsx', 'csv') 
    df.to_csv(output_file, sep="\t", index=False)
    if logger is not None:
        logger.info('converted {input} to {output}'.format(input=input_file,output=output_file))
    return output_file


def find_csv(input_path, file_ending='*.csv'):
    import fnmatch
    csv_list = []
    for file in os.listdir(input_path):
        if fnmatch.fnmatch(file, file_ending):
            csv_list.append(os.path.join(input_path, file))
    if 1==len(csv_list): return csv_list[0]
    if 0==len(csv_list): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), input_path+'/'+file_ending)
    if 1<len(csv_list): raise Exception("There is more than one csv-file")

def build_urn(s): 
    roman_mapping = {'I': '1', 'II': '2'} 
    parts = re.split(r'\s+', s) 
    if re.search(r'Mar[ck]ulf', s): 
        coll_name = 'marculf' 
        if 'Incipit' in s: 
            form_num = roman_mapping[parts[1]] + '_incipit' 
        elif 'Capitula' in s: 
            form_num = roman_mapping[parts[1]] + '_capitula' 
        elif 'Praefatio' in s: 
            form_num = 'form000' 
        elif 'Ergänzung 2' in s:
            form_num = 'form3_2_001'
        elif 'Ergänzung' in s:
            erg_groups = re.search(r'(\d),(\d)', s)
            form_num = 'form3_' + erg_groups.group(1) + '_' + '{:03}'.format(int(erg_groups.group(2)))
        else: 
            book, num = parts[1].split(',') 
            form_num = 'form' + roman_mapping[book] + '_{:03}'.format(int(num)) 
    elif 'Flavigny' in s:
        coll_name = 'flavigny'
        if 'Pa+Ko' in s:
            form_num_part = 'form1_'
        elif 'Ko' in s:
            form_num_part = 'form3_'
        else:
            form_num_part = 'form2_'
        if 'Capitula' in s: 
            form_num = form_num_part.replace('form', '') + 'capitula'
        else:
            num_split = re.search(r'(\d+) ?(\D?)$', s)
            form_num = form_num_part + '{:03}'.format(int(num_split.group(1)))
            if num_split.group(2):
                form_num = form_num + num_split.group(2)
    else:
        coll_name = parts[0].lower() 
        if re.search(r'Praefatio|Titel', s): 
            form_num = 'form000' 
        elif 'Capitula' in s: 
            form_num = '0_capitula' 
        elif 'Weltzeitalter' in s: 
            form_num = 'computus' 
        elif 'Tours Ergänzung 1' in s:
            form_num = 'form2_001'
        elif 'Tours Ergänzung 2' in s:
            form_num = 'form2_002'
        else: 
            num_parts = re.search(r'(\d+)(\D*)', parts[1]) 
            form_num = 'form' + '{:03}'.format(int(num_parts.group(1))) 
            if num_parts.group(2): 
                form_num += '_' + num_parts.group(2).strip('()') 
    return '.'.join([coll_name, form_num, 'lat001'])


def build_sigla(s: str, sigla_dict: dict[str, str], logger: logging.Logger) -> str:
    """
    Builds an HTML-formatted string of manuscript sigla.

    This function parses a string of sigla, formats each siglum by wrapping it in HTML <b> tags
    using a provided mapping, and handles alternative sigla enclosed in square brackets.
    Special cases (e.g., sigla with fragments or non-standard endings) are explicitly handled.

    Parameters:
        s (str): A comma-separated string of sigla, potentially with additional sigla (e.g., "M1, Fu† [auch in M2 und M3]").
        sigla_dict (dict[str, str]): Mapping from base sigla to their formatted HTML representations.
        logger (logging.Logger): Logger for reporting unknown sigla.

    Returns:
        str: An HTML-formatted string with bolded sigla.
    """
    possible_additional_sigla_indicator = [' [auch in ']
    split_regular_alternative_sigla = []

    for indicator in possible_additional_sigla_indicator:
        if indicator in s:
            split_regular_alternative_sigla = s.split(indicator)
            s = split_regular_alternative_sigla[0]
            additional_sigla_indicator = indicator
            break  # use first match and exit

    all_sigla = re.split(r',\s+', s)
    formatted_sigla: list[str] = []



    for sig in all_sigla:
        formatted_sigla.append(format_siglum(sig, sigla_dict))

    html_formatted_sigla = ', '.join(formatted_sigla)

    # Handle additional sigla (e.g., " [auch in M2 und M3]")
    if len(split_regular_alternative_sigla) == 2:
        additional_sigla_str = split_regular_alternative_sigla[1].rstrip(']')
        additional_sigla = re.split(r',\s+', additional_sigla_str)

        pre_remainder = additional_sigla_indicator
        for sig in additional_sigla:
            if ' und ' in sig:
                parts = sig.split(' und ')
                html_formatted_sigla += pre_remainder + format_siglum(parts[0], sigla_dict)
                pre_remainder = ' und '
                sig = parts[1]
            html_formatted_sigla += pre_remainder + format_siglum(sig, sigla_dict)
            pre_remainder = ''
        html_formatted_sigla += ']'

    return html_formatted_sigla

def format_siglum(sig: str, sigla_dict: dict[str, str]) -> str:
    """
    Format a single siglum using the dictionary.

    Args:
        sig (str): The siglum to format.
        sigla_dict (dict[str, str]): Mapping from base sigla to HTML representation.

    Returns:
        str: HTML-formatted siglum.
    """
    sig = sig.replace('**', r'\*\*').strip()

    # Handle special cases
    if sig == '(Sb†)':
        pared_sig = 'Sb†'
        remainder = ')'
        pre_remainder = '('
    elif sig == 'Rg1[Fragm.]†':
        pared_sig = 'Rg1[Fragm.]†'
        remainder = ''
        pre_remainder = ''
    # Handle special cases from Tours 1
    elif sig == "(a) Ko2":
        pared_sig = 'Ko2'
        remainder = ''
        pre_remainder = '(a)'
    elif sig == "(b) Ko2":
        pared_sig = 'Ko2'
        remainder = ''
        pre_remainder = '(b)'
    else:
        pre_remainder = ''
        if sig == 'Fu†':
            pared_sig = 'Fu†'
            remainder = ''
        else:
            # Extract base siglum and suffix
            pared_sig = re.sub(r'(\w+\d*\w?).*', r'\1', sig)
            remainder = re.sub(r'\w+\d*\w?(.*)', r'\1', sig)

            if remainder == '[Fragm.]':
                remainder = '&lt;span class="superscript smaller-text"&gt;[Fragm.]&lt;/span&gt;'

    if pared_sig not in sigla_dict:
        raise KeyError(f"'{pared_sig}' not found in siglen list. "
            "It won't be displayed properly. If it's part of the project, it should appear in the manuscript_collections_md_file. "
            "Otherwise, add it to sigla_html_dict.")

    return pre_remainder + '&lt;b&gt;' + sigla_dict.get(pared_sig, pared_sig) + '&lt;/b&gt;' + remainder

def build_editions(s:str, ed_dict:dict[str:(str,str)], logger) -> str: 
    """
    creates mouse-over tooltips for all editions
    """
    all_eds = re.split(r'; ', s) 
    formatted_eds: list[str] = []
    for ed in all_eds:
        try:
            formatted_eds.append(build_edition(ed, ed_dict, logger))
        except KeyError:
            formatted_eds.append(ed)
  
    return '; '.join(formatted_eds)

def build_edition(edition:str, ed_dict:dict[str:(str,str)], logger) -> str: 
    """
    creates mouse-over tooltips for one edition
    """
    try:
        editor, number = re.split(r': ', edition)
        formatted_editor = editor
        editor = editor.strip().lstrip()
        biblio = ed_dict.get(editor, editor)
        if len(biblio) == 2:
            formatted_editor = biblio[0]
            biblio = biblio[1]
        if editor not in ed_dict:
            logger.warning('"{}" not found in the list of editors'.format(editor))
        
        return '&lt;span data-toggle="tooltip" id="{editor}" data-html="true" data-container="body" title="{biblio}"&gt;&lt;b&gt;{formatted_editor}&lt;/b&gt;&lt;/span&gt;: {form_number}'.format(editor=editor, form_number=number, biblio=biblio, formatted_editor=formatted_editor)
    except ValueError:
        found_at_least_edition = False
        for w in edition.split():
            if w in ed_dict:
                edition = re.sub(w, '&lt;span data-toggle="tooltip" id="{editor}" data-html="true" data-container="body" title="{biblio}"&gt;&lt;b&gt;{editor}&lt;/b&gt;&lt;/span&gt;'.format(editor=w, biblio=ed_dict[w]), edition)
                found_at_least_edition = True
        if not found_at_least_edition: raise KeyError
        return edition

def build_zaehlung(cell:str, sigla_html_dict, ed_bib_info, logger) -> str:
    zaehlung_separator = " "
    zaehlung_components: list[str] = []
    
    for component in cell.split(zaehlung_separator):
        try:
            zaehlung_components.append(format_siglum(component, sigla_dict=sigla_html_dict)) 
        except KeyError:
            try:
                zaehlung_components.append(build_edition(component, ed_bib_info, logger))
            except KeyError:
                zaehlung_components.append(component)

    return zaehlung_separator.join(zaehlung_components)


def get_csv(input_path:str,logging) -> str:
    if not 'csv' in input_path:
        try:
            return find_csv(input_path)
        except FileNotFoundError:
            return xslsx_to_csv(input_path, logging)
    else:
        return input_path
def make_temp_id(title:str) -> str:
    """
    workaround method for mapping a title to an identifier
    Should be solved otherwise in the future
    """
    title_components = title.split(' ')
    match len(title_components):
        case 0 | 1:
            raise ValueError("{} has too few information.".format(title))
        # No subcorpus
        case 2:
            corpus = title_components[0].lower()
            number = title_components[1]
            number_match = re.match(r'^(\d+)\((\w+)\)$', number)
            #40(A) -> (040, A)
            if number_match:
                number, letter = number_match.groups()
                number = number.zfill(3)+'_'+letter
            else:
                number = number.zfill(3)
            identifier="urn:cts:formulae:{corpus}.form_{number}.lat001".format(corpus=corpus , number=number)
            return identifier
        case 3 | 4:
            corpus = title_components[0].lower()
            subcorpus = title_components[1].lower()
            number = title_components[2].zfill(3)
            identifier="urn:cts:formulae:{corpus}.form_{subcorpus}_{number}.lat001".format(corpus=corpus , subcorpus=subcorpus, number=number)
            return identifier
        case _:
            raise ValueError("{} has too much information.".format(title))

import csv

def read_limited_csv(file_path: str, csv_column_limit: int) -> list[list[str]]:
    """
    Reads a CSV file and returns only the first CSV_COLUMN_LIMIT columns of each row.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        list[list[str]]: A list of rows, each row being a list of up to CSV_COLUMN_LIMIT strings.
    """
    rows = []
    with open(file_path, newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        for row in reader:
            rows.append(row[:csv_column_limit+1])
    return rows

def check_apparatus_notes(SEPERATOR_TOKEN, xml_string, rows, logger):
    number_of_separator_tokens = xml_string.count(SEPERATOR_TOKEN)
    number_of_documents = len(rows[1:])
    if SEPERATOR_TOKEN not in xml_string:
        logger.warning("No {SEPERATOR_TOKEN} found in {corpus}. Possible indicator for an incomplete reading from the input.")
    elif number_of_documents >= number_of_separator_tokens: 
        logger.warning(f"Only found {number_of_separator_tokens} {SEPERATOR_TOKEN} in {number_of_documents} documents. This number seems too low and is a possible indicator for an incomplete reading from the input.")
    else:
        logger.info(f"Found {number_of_separator_tokens} {SEPERATOR_TOKEN} in {number_of_documents} documents. This number seems ok and indicates a complete reading from the input.")





def main():
    logger = get_logger()
    logger.setLevel('DEBUG')
    input_path = argv[1]
    formulae_collections_md_file = argv[2]
    manuscript_collections_md_file = argv[3]
    corpus_name = os.path.split(input_path)[-1]
    # Number of columns from the CSV to consider during processing.
    csv_column_limit: int = 3
    output_folder_hss_editionen = '/home/thorben.schomacker/git/scripts/formel_transform/output/{corpus}/hss_editionen.xml'.format(corpus=corpus_name) #argv[3]

    input_encoding = 'utf-8'

    csv_file = get_csv(input_path,logging)

    logger.info('csv-file: '+csv_file)

    ns = {'tei': 'http://www.tei-c.org/ns/1.0', 'cpt': 'http://purl.org/capitains/ns/1.0#', 
          'dc': 'http://purl.org/dc/elements/1.1/', 'dct': 'http://purl.org/dc/terms/', 'bib': 'http://bibliotek-o.org/1.0/ontology/'}

    ed_bib_info = {'Zeu': ('Zeu', 'Zeumer, Karl: Formulae Merowingici et Karolini aevi, Hannover 1882.'),
                'Zeua': ('Zeu&lt;span class="verso-recto"&gt;a&lt;/span&gt;', 'Zeumer, Karl: Über die älteren fränkischen Formelsammlungen, in: Neues Archiv der Gesellschaft für ältere deutsche Geschichtskunde 6 (1881), S. 9–115.'),
                'Udd': ('Udd', 'Uddholm, Alf: Marculfi formularium libri duo, 1962 (Collectio scriptorum veterum Upsaliensis).'),
                'Lin': ('Lin', 'Lindenbrog, Friedrich: Codex legum antiquarum. In quo continentur Leges Wisigothorum, Edictum Theodorici, Lex Burgundionum, Lex Allamannorum, Lex Baiuvariorum, Decretum Tassilonis, Lex Ripuariorum, Lex Saxonum, Lex Angliorum, Lex Frisionum, Lex Langobardorum, Constitutiones siculae, Capitulare Caroli, quibus accedunt Formulae solennes priscae publicorum privatorumque negotium, Frankfurt a.M. 1613'),
                'Roz': ('Roz', "Rozière, Eugène de: Recueil des formules usitées dans l'empire des Francs du Ve au Xe siècle, Paris 1859-1871."),
                'Dav/Fou': ('Dav/Fou', 'Davies, Wendy und Paul Fouracre: The settlement of disputes in early medieval Europe, Cambridge 1986.'),
                'Roc': ('Roc', 'Rockinger, Ludwig von (Hg.): Drei Formelsammlungen aus der Zeit der Karolinger. Aus Münchner Handschriften mitgetheilt, München 1858.'),
                'Mab': ('Mab', 'Mabillon, Jean: Librorum De Re Diplomatica Supplementum : In Quo Archetypa In His Libris pro regulis proposita, ipsaeque regulae denuo confirmantur, novisque speciminibus et argumentis et illustrantur, Paris 1704.'),
                'Rio': ('Rio', 'Rio, Alice: The formularies of Angers and Marculf: Two Merovingian legal handbooks, Liverpool 2008 (Translated texts for historians 46).'),
                'Par': ('Par', "Pardessus, Jean-Marie: Notice sur les manuscrits de formules relatives au droit observé dans l'Empire des Francs, suivie de quatorze formules inédites, in: Bibliothèque de l’école des chartes 4 (1843), S. 1-22."),
                'Bis': ('Bis', 'Bischoff, Bernhard: Epitaphienformeln für Äbtissinnen (Achtes Jahrhundert), in: Ders. (Hg.), Anecdota Novissima. Texte des vierten bis sechszehnten Jahrhunderts, Stuttgart 1984, S. 152'),
                'Wal': ('Wal', 'Les cinq épîtres rimées dans l’appendice des Formules de Sens: Codex Parisinus Latinus 4627, fol. 27v–29r. La querelle des évêques Frodebert et Importun (an 665/666), hg. von Gerard Walstra (Leiden 1962).'),
                'Tyr': ('Tyr', 'V. A. Tyrrell, Merovingian Letters and Letter Writers (Turnhout 2019), S. 70-80.'),
                'Bal': ('Bal', 'Capitularia regum Francorum. Additae sunt Marculfi monachi et aliorum formulae veteres et notae doctissimorum virorum, 2 Bde., hg. von Étienne Baluze (Paris 1677).'),
                'Bou': ('Bou', 'Cinq formules rhytmées et assonancées du VIIe siècle, hg. von Anatole Boucherie (Montpellier/Paris 1867).'),
                'Sha': ('Sha', 'D. Shanzer, The tale of Frodebert’s tail, in: Dickey, E., Chahoud, A. (Hgg.), Colloquial and Literary Latin (Cambridge 2010), 377–405.')}




    form_ms_ed_xml = E.xml()

    rows = read_limited_csv(csv_file, csv_column_limit)
    if len(rows)==0: raise ValueError('{} appears to be empty, since it has no rows'.format(csv_file))
    # Map titles to URNs
    form_coll_md = etree.parse(formulae_collections_md_file)
    title_id_dict = dict()
    for f_c in form_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
        form_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(formulae_collections_md_file), f_c.get('path')))
        if not os.path.isfile(form_corp_md_path): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), form_corp_md_path)
        form_corp_md = etree.parse(form_corp_md_path)
        database_entries = form_corp_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns)
        if len(database_entries)==0: logger.warning('{} entries found within {}'.format(len(database_entries),form_corp_md_path))
        for f_corp in database_entries:
            form_md_path = os.path.normpath(os.path.join(os.path.dirname(form_corp_md_path), f_corp.get('path')))
            if not os.path.isfile(form_md_path): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), form_md_path)
            form_md = etree.parse(form_md_path)
            for c in form_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
                for t in c.xpath('./dc:type/text()', namespaces=ns):
                    if t  == 'cts:edition':
                        identifier = c.xpath('./cpt:identifier/text()', namespaces=ns)[0]
                        
                        key_1 = re.sub(r' \(lat\).*', '', c.xpath('./dc:title/text()', namespaces=ns)[0])
                        title_id_dict[key_1] = identifier

                        key_2=c.xpath('./dc:title/text()', namespaces=ns)[0].replace(' (lat)', '')
                        title_id_dict[key_2] = identifier
    if len(title_id_dict) == 0: logger.error('No title ids found. This will cause an empty result file.') 

    # Map MS sigla to the HTML needed to show them properly
    if not os.path.isfile(manuscript_collections_md_file): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), manuscript_collections_md_file)
    ms_coll_md = etree.parse(manuscript_collections_md_file)
    sigla_html_dict = {
        'Fu†': '&lt;span data-toggle="tooltip" data-boundary="window" id="Fu-verloren-note-tooltip" data-container="body" title="Verlorene Handschrift aus Fulda vgl. Bibliothekskatalog Fulda 16. Jhd. (Vatikan BAV Pal. Lat. 1928) Nr. 238"&gt;&lt;a href="https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_1928/0099/image,info" target="_blank"&gt;Fu† ↗&lt;/a&gt;&lt;/span&gt;',
        'Rg1[Fragm.]†': '&lt;span data-toggle="tooltip" data-boundary="window" id="Rg1-verloren-note-tooltip" data-container="body" title="Regensburg, Staatliche Bibliothek, Inc. 2° 43 (Fragment aus St.Emmeram)"&gt;Rg&lt;span class="subscript smaller-text"&gt;1&lt;/span&gt; &lt;span class="superscript smaller-text"&gt;[Fragm.]†&lt;/span&gt; &lt;/span&gt;',
        # source: /FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Die Marculfsammlung Einleitung_Stand_2025-04-11.docx
        #'Sb†': 'Verlorene Handschrift aus Straßburg [vielleicht Straßburg, ehemalige Stadtbibliothek, C. V. 6†]',
        'Sb†': '&lt;span data-toggle="tooltip" data-boundary="window" id="Sb-verloren-note-tooltip" data-container="body" title="Verlorene Handschrift aus Straßburg [vielleicht Straßburg, ehemalige Stadtbibliothek, C. V. 6†]"&gt;Sb&lt;span class="superscript smaller-text"&gt; † &lt;/span&gt; &lt;/span&gt;'
        #'(Sb†)': '&lt;span data-toggle="tooltip" data-boundary="window" id="Sb-verloren-note-tooltip" data-container="body" title="Verlorene Handschrift aus ???"&gt;&lt;a href="" target="_blank"&gt; ( Sb &lt;span class="subscript smaller-text &gt; † &lt;/span&gt; ) ↗&lt;/a&gt;&lt;/span&gt;'
        }
    for f_c in ms_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
        ms_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(manuscript_collections_md_file), f_c.get('path')))
        if not os.path.isfile(ms_corp_md_path): raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), ms_corp_md_path)
        ms_corp_md = etree.parse(ms_corp_md_path)
        ms_title = ms_corp_md.xpath('/cpt:collection/dc:title/text()', namespaces=ns)[0]
        ms_siglum = ms_corp_md.xpath('/cpt:collection/cpt:structured-metadata/bib:AbbreviatedTitle/text()', namespaces=ns)[0].replace('class="manuscript-number"', 'class="subscript smaller-text"').replace('class="verso-recto"', 'class="superscript smaller-text"')
        ms_html = '&lt;span data-toggle="tooltip" data-boundary="window" id="{htmlID}" data-container="body" title="{ms_title}"&gt;{ms_siglum}&lt;/span&gt;'.format(htmlID=re.sub(R'<[^>]+>', '', ms_siglum) + '-note-tooltip', ms_title=ms_title, ms_siglum=ms_siglum.replace('<', '&lt;').replace('>', '&gt;'))
        sigla_html_dict[re.sub(r'<[^>]+>', '', ms_siglum)] = ms_html


    
    SEPERATOR_TOKEN = '**'
    for r in rows[1:]:
        #cells = r.strip().split('\t')
        cells = r
        if 0 < len(cells):
            info_string = ""
            if 1 < len(cells):
                sigla = build_sigla(cells[1].strip(), sigla_html_dict, logger)
                # contains information on editions
                if 2 < len(cells):
                    info_string = sigla + SEPERATOR_TOKEN + build_editions(cells[2], ed_bib_info, logger)
                    # contains column with Zählung
                    if 3 < len(cells):
                        info_string += SEPERATOR_TOKEN + SEPERATOR_TOKEN.join([build_zaehlung(cell, sigla_html_dict, ed_bib_info, logger) for cell in cells[3:]])
                        # contains column with Zählung
                        if 4 < len(cells):
                            info_string += SEPERATOR_TOKEN + SEPERATOR_TOKEN.join(cells[4:])
            cells[0] = re.sub(r'Flavigny Pa 7 (\D)', r'Flavigny Pa 7\1', cells[0])
            title = cells[0].strip()
            try:
                obtained_id = title_id_dict[title]
            except KeyError as ke: 
                logger.warning('Did not find the {} in title_id_dict, which is based on {}. If this collection is brand new, this behavior is maybe expected. A temporary id will be generated.'.format(title, formulae_collections_md_file))
                obtained_id=make_temp_id(title)
                #raise ke
            
            form_ms_ed_xml.append(E.formula(info_string, n=obtained_id))
                
        # form_ms_ed_dict[build_urn(formula)] = {'manuscripts': build_sigla(mss), 'editions': build_editions(eds)}
    if len(form_ms_ed_xml) == 0: logger.error('form_ms_ed_xml is empty. This can be caused by a malformatted csv-file.') 

    xml_string = etree.tostring(form_ms_ed_xml, pretty_print=True, encoding='unicode')
    xml_string = xml_string.replace('&amp;', '&')
    # Important to have proper ampersand notations
    xml_string = xml_string.replace('&amplt;', '&lt;')
    xml_string = xml_string.replace('&ampgt;', '&gt;')
    xml_path = csv_file.replace('.csv', '.xml')
    check_apparatus_notes(SEPERATOR_TOKEN, xml_string, rows, logger)

    with open(xml_path, mode='w',encoding='utf-8') as f:
        #json.dump(form_ms_ed_dict, f, ensure_ascii=False, indent='\t')
        f.write(xml_string)
        logger.debug('Done! The file was written to: '+xml_path)

    with open(output_folder_hss_editionen, mode='w+',encoding='utf-8') as f:
        f.write(xml_string)
        logger.info('Done! The file was written to: '+output_folder_hss_editionen)

if __name__ == '__main__':
    main()