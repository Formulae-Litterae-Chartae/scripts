import csv
import json
from sys import argv
import re
import os.path

input_file = argv[1]

if os.path.isfile(argv[1]):
    source = argv[1]
else:
    print(argv[1], 'is not a file.')
    raise FileNotFoundError
    
if len(argv) == 3:
    try:
        with open(argv[2]) as f:
            form_mapping = json.load(f)
    except FileNotFoundError as E:
        print(argv[2], 'is not a file.')
        raise E
    except json.JSONDecodeError as E:
        print(argv[2], 'is not a valid JSON file.')
        raise E
    
corp_mapping = {'Mondsee': ['mondsee', 'rath'], 
                'Passau': ['passau', 'heuwieser'], 
                'Regensburg': ['regensburg', 'wiedemann'],
                'Bünden': ['buenden', 'meyer-marthaler'],
                'Freising': ['freising', 'bitterauf'],
                'Fulda': ['fulda', 'stengel'],
                'Lorsch': ['lorsch', 'gloeckner'],
                'Rätien': ['raetien', 'erhart'],
                'Rheinau': ['zuerich', 'escher'],
                'Salzburg': ['salzburg', 'hauthaler-'],
                'Schäftlarn': ['schaeftlarn', 'weissthanner'],
                'St. Gallen': ['stgallen', 'wartmann'],
                'Weißenburg': ['weissenburg', 'gloeckner'],
                'Zürich': ['zuerich', 'escher'],
                'Zürich, S. Felix und Regula': ['zuerich', 'escher']}

json_output = []
temp_dict = dict()

with open(source) as f:                                         
    res = f.readlines()
    # This assumes that the first two columns of the CSV are given over to the naming of the charter and the rest with the formulaic
    # elements.
    # parts contains the names of the formulaic elements in the first line of the CSV.
    parts = [form_mapping.get(x.strip(), None) for x in res[0].split('\t')]
    # charters are the rows of the CSV that actually contain the charter names and formulaic elements.
    charters = [x.rstrip('\n').split('\t') for x in res[1:]]
    

for row in charters:
    if row[0] not in corp_mapping:
        continue
    codex = '' 
    if row[0] == 'Salzburg': 
        if 'Codex' in row[1]: 
            codex = re.sub(r'.+Codex (\w)', r'\1', row[1]).lower() 
        else: 
            codex = 'a' 
    number = re.sub(r'(?:nr.)?\s*(\d+).*', r'\1', row[1].lower()) 
    file_name = '{coll}/{ed}{codex}{num:04}/{coll}.{ed}{codex}{num:04}.lat001'.format(coll=corp_mapping[row[0]][0], codex=codex, ed=corp_mapping[row[0]][1], num=int(number)) 
    if number == '784' and row[0] == 'Freising':
        if '784a' in row[1]:
            file_name = 'freising/bitterauf0784/freising.bitterauf0784.lat003'
        else:
            file_name = 'freising/bitterauf0784/freising.bitterauf0784.lat004'
    if file_name not in temp_dict:
        temp_dict[file_name] = dict()
    for i, col in enumerate(row): 
        if parts[i] and parts[i] not in ['Überlieferung', 'Nummer + Seite'] and col: 
            split_val = re.split(r'\s*[\[\{]…\.? ?[\]\[9]\s*|\s*\[\.+[ \-]?[\]\}]\s*', col)
            if parts[i] in temp_dict[file_name]:
                temp_dict[file_name][parts[i]] += [x for x in split_val if x]
            else:
                temp_dict[file_name][parts[i]] = [x for x in split_val if x]

for k, v in temp_dict.items():
    v.update({'file': k})
    json_output.append(v)

with open(os.path.splitext(input_file)[0] + '.json', mode="w") as f: 
    json.dump(json_output, f, ensure_ascii=False, indent='\t')
