from collections import defaultdict 
from sys import argv
import os
from json import dump
import re

try:
    with open(argv[1]) as f:
        s = f.readlines()
except IndexError as E:
    print('\n**Please input the Pyrrha output file as the first argument when calling this command.**\n')
    raise(E)
except Exception as E:
    raise E

result_dir = os.path.join(os.path.dirname(argv[1]), 'results')
os.makedirs(result_dir, exist_ok=True)
lem_to_lem_mapping = defaultdict(set)
inflected_to_primary_lem = dict()
inflected_to_lem_mapping = defaultdict(set)
formula = 'UNK'

for line in s[1:]: 
    if line.startswith('**'):
        formula = line.strip().split('\t')[0].strip('*')
        inflected_to_primary_lem[formula] = list()
    if not line.startswith('**'): 
        parts = line.strip().lower().split('\t') 
        if not re.search(r'\w', parts[0]):
            continue
        display_lem = parts[1]
        if '=' in parts[1]:
            primary_lem = parts[1].split('=')[0].split('/')[0]
            lem_parts = parts[1].split('=')[0].split('/') + parts[1].split('=')[1].split('+')
        elif '-' in parts[1]:
            primary_lem = parts[1].split('-')[0]
            lem_parts = parts[1].split('-')[1].split('+')
            display_lem = parts[1].split('-')[1]
        else:
            primary_lem = parts[1].split('/')[0]
            lem_parts = parts[1].split('/')
        lem_parts = [x.split('/') for x in lem_parts] 
        for lem_part in lem_parts:
            if len(lem_part) > 1: 
                for i, l in enumerate(lem_part[1:]): 
                    lem_to_lem_mapping[l].update([primary_lem])
            if lem_part[0] != primary_lem:
                lem_to_lem_mapping[lem_part[0]].update([primary_lem])
        inflected_to_primary_lem[formula].append((parts[0], primary_lem, display_lem))
        inflected_to_lem_mapping[parts[0]].update([primary_lem])
                
for k, v in lem_to_lem_mapping.items():
    lem_to_lem_mapping[k] = list(v)
for k, v in inflected_to_lem_mapping.items():
    inflected_to_lem_mapping[k] = list(v)
            
dest_file = os.path.splitext(argv[1])[0] + '_lem_to_lem_mapping.json'
dest_file_2 = os.path.splitext(argv[1])[0] + '_inflected_to_lem_mapping.json'

with open(dest_file, mode="w") as f:
    dump(lem_to_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')
with open(dest_file_2, mode="w") as f:
    dump(inflected_to_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')

for form, mapping in inflected_to_primary_lem.items():
    with open(os.path.join(result_dir, form + '.txt'), mode="w") as f:
        f.write('\n'.join(['{}\t{}\t{}'.format(x, y, z) for x, y, z in mapping]))
