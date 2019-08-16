from json import dump, load, JSONDecodeError
from string import punctuation
from sys import argv
import re
from os.path import isfile


punc = punctuation.replace(']', '')

# source should be a CSV file that contains the names of each charter to be analyzed and then each column after the name
# should contain the contents of one formulaic section of that charter.
if isfile(argv[1]):
    source = argv[1]
else:
    print(argv[1], 'is not a file.')
    raise FileNotFoundError

# This should be the JSON file to which the results should be saved.
dest = argv[2]
if len(argv) == 4:
    try:
        with open(argv[3]) as f:
            form_mapping = load(f)
    except FileNotFoundError as E:
        print(argv[3], 'is not a file.')
        raise E
    except JSONDecodeError as E:
        print(argv[3], 'is not a valid JSON file.')
        raise E
    
# This pattern should extract the name of the charter from the correct column in the CSV. Change this as necessary
pat = re.compile(r'(?:Nr. )?(\d+)(\.lat00\d)?')

# coll_mapping maps the names of the charter collections given in the CSV to the different parts of their URNs
# each value is a list with the first member being the first part of the URN, e.g., 'mondsee' in mondsee.rath0001.lat001
# the second member is then the first part of the second part of the URN, e.g., 'rath' in the URN above.
coll_mapping = {'Mondsee': ['mondsee', 'rath'], 'Passau': ['passau', 'heuwieser'], 'Regensburg': ['regensburg', 'wiedemann']}

charter_forms = []

with open(source) as f:                                         
    res = f.readlines()
    # This assumes that the first two columns of the CSV are given over to the naming of the charter and the rest with the formulaic
    # elements.
    # parts contains the names of the formulaic elements in the first line of the CSV.
    parts = [form_mapping.get(x.strip(), x.strip()) for x in res[0].split('\t')[2:]]
    # charters are the rows of the CSV that actually contain the charter names and formulaic elements.
    charters = [x.rstrip('\n').split('\t') for x in res[1:]]

for c in charters:
    # This assumes that the second column contains the number while the first contains the name of the charter collection
    nr = re.search(pat, c[1])
    # Builds the filepath from the coll_mapping and the charter nr
    file = '/'.join(coll_mapping[c[0].strip()]) + '{:004}'.format(int(nr[1])) + '/' + '.'.join(coll_mapping[c[0].strip()]) + '{:004}'.format(int(nr[1])) + nr.groups('.lat001')[1]
    form_part_dict = {'file': file}                       
    for i, p in enumerate(c[2:]):                                              
        if p:
            # The split here is on the separator that was used in the CSV to denote when a single formulaic part is 
            # interrupted by another. So if the dating of the charter comes in the middle of the arenga, the arenga would
            # have this separator to denote that something else comes in this place.
            form_part_dict[parts[i]] = re.split(r' \[\.+\] | \[…\] ', p)     
    charter_forms.append(form_part_dict)

with open(dest, mode="w") as f:                            
    dump(charter_forms, f, ensure_ascii=False, indent='\t')
