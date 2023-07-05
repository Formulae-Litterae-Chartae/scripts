import os
from glob import glob

xmls = glob('/media/FORMAKAD/Werkstatt/Formelsammlungen/**/*.xml', recursive=True)
ctes = glob('/media/FORMAKAD/Werkstatt/Formelsammlungen/**/*.cte', recursive=True)

cte_dict = {os.path.basename(x).replace('.cte', ''): os.path.getmtime(x) for x in ctes}
xml_dict = {os.path.basename(x).replace('.xml', ''): os.path.getmtime(x) for x in xmls}

need_updates = list()

for xml, xml_time in xml_dict.items():
    if cte_dict.get(xml, 0) > xml_time:
        need_updates.append(xml)

with open('/home/matt/results/formulae_xml_files_to_update.txt', mode='w') as f:
    f.write('\n'.join(need_updates))
