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
    
for r in rows[1:]:
    row_parts = r.split('\t')
    form_ms_ed_xml.append(E.formula('**'.join(row_parts[1:]), n=title_id_dict[row_parts[0]]))
    # form_ms_ed_dict[build_urn(formula)] = {'manuscripts': build_sigla(mss), 'editions': build_editions(eds)}
    
xml_string = etree.tostring(form_ms_ed_xml, pretty_print=True, encoding='unicode')
xml_string = xml_string.replace('&amp;', '&')

with open(csv_file.replace('.csv', '.xml'), mode='w') as f:
    #json.dump(form_ms_ed_dict, f, ensure_ascii=False, indent='\t')
    f.write(xml_string)
