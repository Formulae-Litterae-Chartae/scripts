import re
from sys import argv
from lxml.builder import E
from lxml import etree
import os

csv_file = argv[1]
formulae_collections_md_file = argv[2]
manuscript_collections_md_file = argv[3]

ns = {'tei': 'http://www.tei-c.org/ns/1.0', 'cpt': 'http://purl.org/capitains/ns/1.0#', 'dc': 'http://purl.org/dc/elements/1.1/', 'dct': 'http://purl.org/dc/terms/', 'bib': 'http://bibliotek-o.org/1.0/ontology/'}

ed_bib_info = {'Zeu': 'Zeumer, Karl: Formulae Merowingici et Karolini aevi, Hannover 1882.', 
               'Udd': 'Uddholm, Alf: Marculfi formularium libri duo, 1962 (Collectio scriptorum veterum Upsaliensis).', 
               'Lin': 'Lindenbrog, Friedrich, Codex legum antiquarum. In quo continentur Leges Wisigothorum, Edictum Theodorici, Lex Burgundionum, Lex Allamannorum, Lex Baiuvariorum, Decretum Tassilonis, Lex Ripuariorum, Lex Saxonum, Lex Angliorum, Lex Frisionum, Lex Langobardorum, Constitutiones siculae, Capitulare Caroli, quibus accedunt Formulae solennes priscae publicorum privatorumque negotium, Frankfurt a.M. 1613',
               'Roz': "Rozière, Eugène de: Recueil des formules usitées dans l'empire des Francs du Ve au Xe siècle, Paris 1859-1871.",
               'Dav/Fou': 'Davies, Wendy und Paul Fouracre: The settlement of disputes in early medieval Europe, Cambridge 1986.'}

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
        else: 
            book, num = parts[1].split(',') 
            form_num = roman_mapping[book] + '_{:03}'.format(int(num)) 
    else:
        coll_name = parts[0].lower() 
        if 'Praefatio' in s: 
            form_num = 'form000' 
        elif 'Capitula' in s: 
            form_num = '0_capitula' 
        elif 'Weltzeitalter' in s: 
            form_num = 'computus' 
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
        formatted_sigla.append(sigla_dict.get(sig, sig))
        if sig not in sigla_dict:
            print(sig + ' not found in siglen list')
    return ', '.join(formatted_sigla)

def build_editions(s, ed_dict): 
    all_eds = re.split(r'; ', s) 
    formatted_eds = list() 
    for ed in all_eds: 
        editor, number = re.split(r': ', ed) 
        formatted_eds.append('&lt;span data-toggle="tooltip" id="{editor}" data-html="true" data-container="body" title="{biblio}"&gt;&lt;b&gt;{editor}&lt;/b&gt;&lt;/span&gt;: {form_number}'.format(editor=editor, form_number=number, biblio=ed_dict.get(editor, editor)))
        if editor not in ed_dict:
            print(editor + ' not found in the list of editors')
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
                    title_id_dict[c.xpath('./dc:title/text()', namespaces=ns)[0].replace(' (lat)', '')] = c.xpath('./cpt:identifier/text()', namespaces=ns)[0]
                    
# Map MS sigla to the HTML needed to show them properly
ms_coll_md = etree.parse(manuscript_collections_md_file)
sigla_html_dict = dict()
for f_c in ms_coll_md.xpath('/cpt:collection/cpt:members/cpt:collection', namespaces=ns):
    ms_corp_md_path = os.path.normpath(os.path.join(os.path.dirname(manuscript_collections_md_file), f_c.get('path')))
    ms_corp_md = etree.parse(ms_corp_md_path)
    ms_title = ms_corp_md.xpath('/cpt:collection/dc:title/text()', namespaces=ns)[0]
    ms_siglum = ms_corp_md.xpath('/cpt:collection/cpt:structured-metadata/bib:AbbreviatedTitle/text()', namespaces=ns)[0].replace('class="manuscript-number"', 'class="subscript smaller-text"').replace('class="verso-recto"', 'class="superscript smaller-text"')
    ms_html = '&lt;span data-toggle="tooltip" data-boundary="window" id="{htmlID}" data-container="body" title="{ms_title}"&gt;{ms_siglum}&lt;/span&gt;'.format(htmlID=re.sub(R'<[^>]+>', '', ms_siglum) + '-note-tooltip', ms_title=ms_title, ms_siglum=ms_siglum.replace('<', '&lt;').replace('>', '&gt;'))
    sigla_html_dict[re.sub(R'<[^>]+>', '', ms_siglum)] = ms_html
    
for r in rows[1:]:
    formula, mss, eds = r.strip().split('\t')
    form_ms_ed_xml.append(E.formula(E.manuscripts(build_sigla(mss, sigla_html_dict)), E.editions(build_editions(eds, ed_bib_info)), n=title_id_dict[formula]))
    # form_ms_ed_dict[build_urn(formula)] = {'manuscripts': build_sigla(mss), 'editions': build_editions(eds)}
    
xml_string = etree.tostring(form_ms_ed_xml, pretty_print=True, encoding='unicode')
xml_string = xml_string.replace('&amp;', '&')

with open(csv_file.replace('.csv', '.xml'), mode='w') as f:
    #json.dump(form_ms_ed_dict, f, ensure_ascii=False, indent='\t')
    f.write(xml_string)
