import os
from glob import glob

directories = ['/media/FORMAKAD/Werkstatt/Formelsammlungen/Angers/Onlineedition/Edition',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Angers/Onlineedition/Uebersetzungen',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Angers/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Auvergne',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Auvergne/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Bourges',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Bourges/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Capitulationes',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Capitulationes/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Ko',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Ko/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Pa',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Pa/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Pa+Ko',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Flavigny/Flavigny Pa+Ko/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf Ergänzungen',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf Ergänzungen/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf I',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf I/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf II',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Marculf/Marculf II/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Tours',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Tours/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Toursüberarbeitung (Vatikan BAV Reg. lat. 1050)',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Toursüberarbeitung (Vatikan BAV Reg. lat. 1050)/Einzeltranskripte',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Weiteres Formelmaterial/Formulae Marculfinae aevi Karolini',
               '/media/FORMAKAD/Werkstatt/Formelsammlungen/Weiteres Formelmaterial/Formulae Marculfinae aevi Karolini/Einzeltranskripte']

ctes = list()
need_updates = list()

for d in directories:
    ctes += glob(d + '/*.cte')

for c in ctes:
    xml = os.path.dirname(c) + '/XML/' + os.path.basename(c).replace('.cte', '.xml').replace(' [Onlineformatierung]', '')
    if not os.path.isfile(xml):
        print('No XML file for', os.path.basename(c))
    else:
        if os.path.getmtime(c) > os.path.getmtime(xml):
            need_updates.append(os.path.basename(c))

with open('/home/matt/results/formulae_xml_files_to_update.txt', mode='w') as f:
    f.write('\n'.join(need_updates))
