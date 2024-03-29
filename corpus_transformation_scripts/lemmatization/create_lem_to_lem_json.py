from collections import defaultdict 
from sys import argv
import os
from json import dump
import re
from glob import glob

if len(argv) < 1:
    print('\n**Please input the Pyrrha output file as the first argument when calling this command.**\n')
    raise IndexError

tsv_files = list()

if os.path.isfile(argv[1]):
    tsv_files.append(argv[1])
    dest_file_pattern = os.path.splitext(argv[1])[0]
elif os.path.isdir(argv[1]):
    tsv_files += glob(os.path.join(argv[1], '*.tsv'))
    dest_file_pattern = os.path.join(argv[1], 'all_files')
else:
    raise SyntaxError('\n**The first argument must be either a .tsv file or a directory containing multiple .tsv files.**\n')

dest_folder = ''
if len(argv) > 2:
    dest_folder = argv[2]

result_dir = os.path.join(os.path.dirname(argv[1]), 'results')
os.makedirs(result_dir, exist_ok=True)
lem_to_lem_mapping = defaultdict(set)
inflected_to_primary_lem = dict()
inflected_to_full_lem_mapping = defaultdict(set)
inflected_to_lem_mapping = defaultdict(set)
inflected_to_full_lemma_charters = defaultdict(set)
inflected_to_full_lemma_formulae = defaultdict(set)
all_lems = set()
formula = 'UNK'
german_lemmas = ['Personenname', 'Ortsname', 'Volksstamm', 'Monatsname', 'Tagesbezeichnung', 'Platzhalter']
german_lemmas += [x.lower() for x in german_lemmas]
all_lines = ['form\tlemma\tPOS\tmorph\n']

for tsv_file in sorted(tsv_files):
    try:
        with open(tsv_file) as f:
            s = f.readlines()
    except Exception as E:
        raise E
    for line in s[1:]: 
        all_lines.append(line)
        if line.startswith('**'):
            formula = line.strip().split('\t')[0].strip('*')
            inflected_to_primary_lem[formula] = list()
        if not line.startswith('**'): 
            full_lem = line.strip().split('\t')[1]
            parts = line.strip().lower().replace('$', '').split('\t') 
            if not re.search(r'\w', parts[0]):
                continue
            display_lem = parts[1]
            if '=' in parts[1]:
                primary_lem = parts[1].split('=')[0].split('/')[0]
                lem_parts = parts[1].split('=')[0].split('/') + parts[1].split('=')[1].split('+')
                if '!' not in primary_lem and '?' not in primary_lem and primary_lem not in german_lemmas:
                    all_lems.add(primary_lem)
            elif '-' in parts[1]:
                primary_lem = parts[1].split('-')[0]
                lem_parts = parts[1].split('-')[1].split('+')
                display_lem = parts[1].split('-')[1]
            else:
                primary_lem = parts[1].split('/')[0]
                lem_parts = parts[1].split('/')
                if '!' not in primary_lem and '?' not in primary_lem and primary_lem not in german_lemmas:
                    all_lems.add(primary_lem)
            lem_parts = [x.split('/') for x in lem_parts] 
            all_lems.update([y for x in lem_parts for y in x if '!' not in y and '?' not in y and y not in german_lemmas])
            for lem_part in lem_parts:
                if len(lem_part) > 1: 
                    for i, l in enumerate(lem_part[1:]): 
                        lem_to_lem_mapping[l].update([primary_lem])
                if lem_part[0] != primary_lem:
                    lem_to_lem_mapping[lem_part[0]].update([primary_lem])
            inflected_to_primary_lem[formula].append((parts[0], primary_lem, display_lem))
            inflected_to_lem_mapping[parts[0]].update([primary_lem])
            inflected_to_full_lem_mapping[parts[0]].update([full_lem])
            if 'formeln' in tsv_file:
                inflected_to_full_lemma_formulae[parts[0]].update([full_lem])
            else:
                inflected_to_full_lemma_charters[parts[0]].update([full_lem])
                
for k, v in lem_to_lem_mapping.items():
    lem_to_lem_mapping[k] = list(v)
for k, v in inflected_to_full_lem_mapping.items():
    inflected_to_full_lem_mapping[k] = list(v)
for k, v in inflected_to_lem_mapping.items():
    inflected_to_lem_mapping[k] = list(v)
for k, v in inflected_to_full_lemma_charters.items():
    inflected_to_full_lemma_charters[k] = list(v)
for k, v in inflected_to_full_lemma_formulae.items():
    inflected_to_full_lemma_formulae[k] = list(v)
            
dest_file = dest_file_pattern + '_lem_to_lem_mapping.json'
dest_file_2 = dest_file_pattern + '_inflected_to_full_lem_mapping.json'
dest_file_3 = dest_file_pattern + '_lemma_list.json'
dest_file_4 = dest_file_pattern + '_inflected_to_full_lem_mapping_charters.json'
dest_file_5 = dest_file_pattern + '_inflected_to_full_lem_mapping_formulae.json'
dest_file_6 = os.path.join(argv[1], 'Formulae+Urkunden.csv')
dest_file_7 = dest_file_pattern + '_inflected_to_lem_mapping.json'

if dest_folder:
    dest_file = os.path.join(dest_folder, 'lem_to_lem.json')
    dest_file_2 = os.path.join(dest_folder, 'inflected_to_lem.json')
    dest_file_3 = os.path.join(dest_folder, 'lemma_list.json')

with open(dest_file, mode="w") as f:
    dump(lem_to_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_2, mode="w") as f:
    dump(inflected_to_full_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_3, mode="w") as f:
    dump(sorted(all_lems), f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_4, mode="w") as f:
    dump(inflected_to_full_lemma_charters, f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_5, mode="w") as f:
    dump(inflected_to_full_lemma_formulae, f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_6, mode="w") as f:
    f.write(''.join(all_lines))
with open(dest_file_7, mode="w") as f:
    dump(inflected_to_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')

for form, mapping in inflected_to_primary_lem.items():
    with open(os.path.join(result_dir, form.replace('.txt', '') + '.txt'), mode="w") as f:
        f.write('\n'.join(['{}\t{}\t{}'.format(x, y, z) for x, y, z in mapping]))
