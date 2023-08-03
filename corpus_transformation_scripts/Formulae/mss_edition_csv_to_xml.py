
import re
from sys import argv
from lxml.builder import E
from lxml import etree
import os

csv_file = argv[1]
formulae_collections_md_file = argv[2]
manuscript_collections_md_file = argv[3]

ns = {'tei': 'http://www.tei-c.org/ns/1.0', 'cpt': 'http://purl.org/capitains/ns/1.0#', 'dc': 'http://purl.org/dc/elements/1.1/', 'dct': 'http://purl.org/dc/terms/', 'bib': 'http://bibliotek-o.org/1.0/ontology/'}

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
               'Bis': ('Bis', 'Bischoff, Bernhard: Epitaphienformeln für Äbtissinnen (Achtes Jahrhundert), in: Ders. (Hg.), Anecdota Novissima. Texte des vierten bis sechszehnten Jahrhunderts, Stuttgart 1984, S. 152')}

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
        elif 'Ergänzungen 2' in s:
            form_num = 'form3_2_001'
        elif 'Ergänzungen' in s:
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

def build_sigla(s, sigla_dict): 
    all_sigla = re.split(r',\s+', s) 
    formatted_sigla = list() 
    for sig in all_sigla: 
        pared_sig = re.sub(r'(\w+\d*\w?).*', r'\1', sig)
        remainder = re.sub(r'\w+\d*\w?(.*)', r'\1', sig)
        if sig == 'Fu†':
            pared_sig = 'Fu†'
            remainder = ''
        formatted_sigla.append('&lt;b&gt;' + sigla_dict.get(pared_sig, pared_sig) + '&lt;/b&gt;' + remainder)
        if pared_sig not in sigla_dict:
            print(pared_sig + ' not found in siglen list')
    return ', '.join(formatted_sigla)

def build_editions(s, ed_dict): 
    all_eds = re.split(r'; ', s) 
    formatted_eds = list() 
    for ed in all_eds: 
        try:
            editor, number = re.split(r': ', ed)
            formatted_editor = editor
            biblio = ed_dict.get(editor, editor)
            if len(biblio) == 2:
                formatted_editor = biblio[0]
                biblio = biblio[1]
            formatted_eds.append('&lt;span data-toggle="tooltip" id="{editor}" data-html="true" data-container="body" title="{biblio}"&gt;&lt;b&gt;{formatted_editor}&lt;/b&gt;&lt;/span&gt;: {form_number}'.format(editor=editor, form_number=number, biblio=biblio, formatted_editor=formatted_editor))
            if editor not in ed_dict:
                print(editor + ' not found in the list of editors')
        except ValueError:
            for w in ed.split():
                if w in ed_dict:
                    ed = re.sub(w, '&lt;span data-toggle="tooltip" id="{editor}" data-html="true" data-container="body" title="{biblio}"&gt;&lt;b&gt;{editor}&lt;/b&gt;&lt;/span&gt;'.format(editor=w, biblio=ed_dict[w]), ed)
            formatted_eds.append(ed)
    return '; '.join(formatted_eds)

form_ms_ed_xml = E.xml()

with open(csv_file) as f:
    rows = f.readlines()

# Map titles to URNs
form_coll_md = etree.parse(formulae_collections_md_file)
title_id_dict = dict()
for f_c in form_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
    form_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(formulae_collections_md_file), f_c.get('path')))
    form_corp_md = etree.parse(form_corp_md_path)
    for f_corp in form_corp_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
        form_md_path = os.path.normpath(os.path.join(os.path.dirname(form_corp_md_path), f_corp.get('path')))
        form_md = etree.parse(form_md_path)
        for c in form_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
            for t in c.xpath('./dc:type/text()', namespaces=ns):
                if t  == 'cts:edition':
                    title_id_dict[re.sub(r' \(lat\).*', '', c.xpath('./dc:title/text()', namespaces=ns)[0])] = c.xpath('./cpt:identifier/text()', namespaces=ns)[0]
                    title_id_dict[c.xpath('./dc:title/text()', namespaces=ns)[0].replace(' (lat)', '')] = c.xpath('./cpt:identifier/text()', namespaces=ns)[0]

# Map MS sigla to the HTML needed to show them properly
ms_coll_md = etree.parse(manuscript_collections_md_file)
sigla_html_dict = {'Fu†': '&lt;span data-toggle="tooltip" data-boundary="window" id="Fu-verloren-note-tooltip" data-container="body" title="Verlorene Handschrift aus Fulda vgl. Bibliothekskatalog Fulda 16. Jhd. (Vatikan BAV Pal. Lat. 1928) Nr. 238"&gt;&lt;a href="https://digi.ub.uni-heidelberg.de/diglit/bav_pal_lat_1928/0099/image,info" target="_blank"&gt;Fu† ↗&lt;/a&gt;&lt;/span&gt;'}
for f_c in ms_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
    ms_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(manuscript_collections_md_file), f_c.get('path')))
    ms_corp_md = etree.parse(ms_corp_md_path)
    ms_title = ms_corp_md.xpath('/cpt:collection/dc:title/text()', namespaces=ns)[0]
    ms_siglum = ms_corp_md.xpath('/cpt:collection/cpt:structured-metadata/bib:AbbreviatedTitle/text()', namespaces=ns)[0].replace('class="manuscript-number"', 'class="subscript smaller-text"').replace('class="verso-recto"', 'class="superscript smaller-text"')
    ms_html = '&lt;span data-toggle="tooltip" data-boundary="window" id="{htmlID}" data-container="body" title="{ms_title}"&gt;{ms_siglum}&lt;/span&gt;'.format(htmlID=re.sub(R'<[^>]+>', '', ms_siglum) + '-note-tooltip', ms_title=ms_title, ms_siglum=ms_siglum.replace('<', '&lt;').replace('>', '&gt;'))
    sigla_html_dict[re.sub(r'<[^>]+>', '', ms_siglum)] = ms_html

for r in rows[1:]:
    cells = r.strip().split('\t')
    if len(cells) > 1:
        info_string = build_sigla(cells[1].strip(), sigla_html_dict) + '**' + build_editions(cells[2], ed_bib_info)
        if len(cells) > 3:
            info_string += '**' + '**'.join(cells[3:])
        cells[0] = re.sub(r'Flavigny Pa 7 (\D)', r'Flavigny Pa 7\1', cells[0])
        form_ms_ed_xml.append(E.formula(info_string, n=title_id_dict[cells[0].strip()]))
    # form_ms_ed_dict[build_urn(formula)] = {'manuscripts': build_sigla(mss), 'editions': build_editions(eds)}

xml_string = etree.tostring(form_ms_ed_xml, pretty_print=True, encoding='unicode')
xml_string = xml_string.replace('&amp;', '&')

with open(csv_file.replace('.csv', '.xml'), mode='w') as f:
    #json.dump(form_ms_ed_dict, f, ensure_ascii=False, indent='\t')
    f.write(xml_string)
