import re
from sys import argv
from lxml.builder import E
from lxml import etree

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

def build_sigla(s): 
    all_sigla = re.split(r',\s+', s) 
    formatted_sigla = list() 
    for sig in all_sigla: 
        parts = re.search(r'(\D+)(\d+)(\D*)', sig) 
        sigla = parts.group(1) + '&lt;span class="subscript smaller-text"&gt;{}&lt;/span&gt;'.format(parts.group(2)) 
        if parts.group(3).strip(): 
            sigla += '&lt;span class="verso-recto"&gt;{}&lt;/span&gt;'.format(parts.group(3)) 
        formatted_sigla.append(sigla) 
    return ', '.join(formatted_sigla)

def build_editions(s): 
    all_eds = re.split(r'; ', s) 
    formatted_eds = list() 
    for ed in all_eds: 
        editor, number = re.split(r': ', ed) 
        formatted_eds.append('&lt;b&gt;{}&lt;/b&gt;: {}'.format(editor, number)) 
    return '; '.join(formatted_eds)

form_ms_ed_xml = E.xml()

with open(argv[1]) as f:
    rows = f.readlines()
    
for r in rows:
    formula, mss, eds = r.strip().split('\t')
    form_ms_ed_xml.append(E.formula(E.manuscripts(build_sigla(mss)), E.editions(build_editions(eds)), n=build_urn(formula)))
    # form_ms_ed_dict[build_urn(formula)] = {'manuscripts': build_sigla(mss), 'editions': build_editions(eds)}
    
xml_string = etree.tostring(form_ms_ed_xml, pretty_print=True, encoding='unicode')
xml_string = xml_string.replace('&amp;', '&')

with open(argv[1].replace('.csv', '.xml'), mode='w') as f:
    #json.dump(form_ms_ed_dict, f, ensure_ascii=False, indent='\t')
    f.write(xml_string)
