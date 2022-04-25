from collections import Counter, defaultdict
from glob import glob
from sys import argv
from datetime import date
import json

folder = argv[1]

files = glob(folder + '/urls_*.txt')

d = defaultdict(Counter)
errors = list()

for file in files:
    with open(file) as f:
        lines = f.read().strip().split('\n')
    for line in lines:
        params = line.split('?')[-1]
        for full_p in params.split('&'):
            try:
                p, v = full_p.split('=')
                d[p].update([v])
            except:
                errors.append('Could not parse URL ' + line)
                continue
            
with open(folder + '/collation_{}.json'.format(str(date.today())), mode='w') as f:
    json.dump(d, f, ensure_ascii=False, indent='\t')
    
if errors:
    with open(folder + '/errors_{}.txt'.format(str(date.today())), mode='w') as f:
        f.write('\n'.join(errors))
