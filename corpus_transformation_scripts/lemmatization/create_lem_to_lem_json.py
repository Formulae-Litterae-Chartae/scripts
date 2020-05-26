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
formula = 'UNK'

for line in s[1:]: 
    if line.startswith('**'):
        formula = line.strip().split('\t')[0].strip('*')
        inflected_to_primary_lem[formula] = list()
    if not line.startswith('**'): 
        parts = line.strip().split('\t') 
        if not re.search(r'\w', parts[0]):
            continue
        lem_parts = parts[1].split('/') 
        if len(lem_parts) > 1: 
            for i, l in enumerate(lem_parts[1:]): 
                lem_to_lem_mapping[l].update(lem_parts[:i + 1])
        inflected_to_primary_lem[formula].append((parts[0], lem_parts[0]))
                
for k, v in lem_to_lem_mapping.items():
    lem_to_lem_mapping[k] = list(v)
            
dest_file = os.path.splitext(argv[1])[0] + '_lem_to_lem_mapping.json'

with open(dest_file, mode="w") as f:
    dump(lem_to_lem_mapping, f, ensure_ascii=False, sort_keys=True, indent='\t')

for form, mapping in inflected_to_primary_lem.items():
    with open(os.path.join(result_dir, form + '.txt'), mode="w") as f:
        f.write('\n'.join(['{}\t{}'.format(x, y) for x, y in mapping]))
