import json
from copy import copy
from collections import defaultdict
from glob import glob
from lxml import etree
import re
import roman

files = [x for x in glob('/home/matt/formulae-corpora/data/**/*.xml', recursive=True) if '__capitains__' not in x]
with open('/home/matt/results/corpus_segmentation/Urkundenarten_Gesamt.json') as f:
    type_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/Gesamtübersicht_Urkundengruppen.json') as f:
    charter_group_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/St_Gallen_Urkundenfamilien.json') as f:
    st_gallen_group_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/Gesamtübersicht_Arengenfamilien_ingest.json') as f:
    arengenfamilien_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/Gesamtübersicht_Überleitungsformelfamilien_ingest.json') as f:
    ueberleitungsformelfamilien_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/Formel_zu_Urkunden_Entsprechungen.json') as f:
    formel_zu_urkunden_dict = json.load(f)
with open('/home/matt/results/corpus_segmentation/Formel_zu_Formel_Entsprechungen.json') as f:
    formel_zu_formel_dict = json.load(f)

all_part_template = list()
all_charter_groups_list = list()
charter_parts_list = list()
st_gallen_groups_template = list()
arengenfamilien_template = list()
ueberleitungsformelfamilien_template = list()
parts_dict = defaultdict(dict)
title_dict = dict()
good_parts = {'Arenga': {'title': 'Arengen'},
              'Poenformel-Vordersatz-': {'part_name': 'Poenformel (Vordersatz)', 'title': 'Poenformel (Vordersatz)'},
              'Poenformel-Strafklausel-': {'part_name': 'Poenformel (Strafklausel)', 'title': 'Poenformel (Strafklausel)'},
              'Stipulationsformel': {},
              'Überleitungsformel': {}}

html_template = """
                    <div class="card">
                        <h3 class="card-header" id="part-PART_HERE">
                            <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#part-collapse-PART_HERE" aria-expanded="true" aria-controls="part-collaps
e-PART_HERE">
                            <h4>TITLE_PART_HERE</h4>
                            </button>
                        </h3>
                        <div id="part-collapse-PART_HERE" class="collapse part-collapse" aria-labelledby="part-category-PART_HERE" data-parent="#partAccordion">
                            <div class="card-body">
                                <table id="PART_HEREPartsTable" class="table table-sm table-hover table-bordered parts-table" aria-label="TITLE_PART_HERE {{ _('Tabelle') }}">
                                    <thead>
                                        <tr>
                                            <th id="PART_HERE-title-charter-column" scope="col">{{ _('Urkunde') }}</th>
                                            <th id="PART_HERE-all-charter-date-column" scope="col">{{ _("Datum") }}</th>
                                            <th id="PART_HERE-type-charter-column" scope="col">
                                                <div class="dropdown">
                                                    <a class="dropdown-toggle text-body" href="#" role="button" data-toggle="dropdown" aria-expanded="false">{{ _('Urkundenart') }}</a>
                                                    <form class="dropdown-menu px-4">
                                                        <div class="form-group m-0">
                                                            <input class="charter-type-filter form-check-input" id="PART_HERE-kauf-checkbox" type="checkbox" value="Kauf"><label class="form-check-label font-weight-normal" for="PART_HERE-kauf-checkbox">Kauf</a>
                                                        </div>
                                                        <div class="form-group m-0">
                                                            <input class="charter-type-filter form-check-input" id="PART_HERE-praestarie-checkbox" type="checkbox" value="Prästarie"><label class="form-check-label font-weight-normal" for="PART_HERE-praestarie-checkbox">Prästarie</a>
                                                        </div>
                                                        <div class="form-group m-0">
                                                            <input class="charter-type-filter form-check-input" id="PART_HERE-prekarie-checkbox" type="checkbox" value="Prekarie"><label class="form-check-label font-weight-normal" for="PART_HERE-prekarie-checkbox">Prekarie</a>
                                                        </div>
                                                        <div class="form-group m-0">
                                                            <input class="charter-type-filter form-check-input" id="PART_HERE-schenkung-checkbox" type="checkbox" value="Schenkung"><label class="form-check-label font-weight-normal" for="PART_HERE-schenkung-checkbox">Schenkung</a>
                                                        </div>
                                                        <div class="form-group m-0">
                                                            <input class="charter-type-filter form-check-input" id="PART_HERE-tausch-checkbox" type="checkbox" value="Tausch"><label class="form-check-label font-weight-normal" for="PART_HERE-tausch-checkbox">Tausch</a>
                                                        </div>
                                                    </form>
                                                </div>
                                            </th>
                                            <th id="PART_HERE-charter-column" scope="col">FORMAT_PART_HERE</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ROWS_HERE
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>"""

row_template = """
                                        <tr>
                                            <td><a class="internal-link" href="{{ url_for('InstanceNemo.r_multipassage', objectIds='URN_HERE', subreferences='all', formpart='PART_HERE') }}">TITLE_HERE</a></td>
                                            <td>DATE_HERE</td>
                                            <td>ART_HERE</td>
                                            <td>TEXT_HERE</td>
                                        </tr>"""

all_group_html_template = """
                    <div class="card">
                        <h3 class="card-header all-group-header" id="part-allCharterGroups">
                            <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#NO_SPACE_GROUP_HERECharterGroupAccordion" aria-expanded="true" aria-controls="allCharterGroupAccordion">
                            <h4>MAIN_GROUP_HERE</h4>
                            </button>
                        </h3>
                        <div class="accordion collapse parts-collapse" id="NO_SPACE_GROUP_HERECharterGroupAccordion">
                        SUB_GROUP_HERE
                        </div>
                    </div>"""

all_subgroup_html_template = """
                                <h3 class="card-header all-group-header" id="part-allCharterGroups-GROUP_HERE">
                                    <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#part-collapse-allCharterGroups-GROUP_HERE" aria-expanded="true" aria-controls="part-collapse-allCharterGroups-GROUP_HERE">
                                    <h5>GROUP_TITLE_HERE DATE_RANGE_HERE</h5>
                                    </button>
                                </h3>
                                <div id="part-collapse-allCharterGroups-GROUP_HERE" class="collapse parts-collapse" aria-labelledby="allCharterGroupTableGROUP_HERE" data-parent="#NO_SPACE_GROUP_HERECharterGroupAccordion">
                                    <div class="card-body">
                                        <table id="allCharterGroupTableGROUP_HERE" class="table table-sm table-hover table-bordered" aria-label="COLLECTION_HERE GROUP_TITLE_HERE">
                                            <thead>
                                                <tr>
                                                    <th id="all-charter-checkbox-column" scope="col"></th>
                                                    <th id="all-charter-title-column" scope="col">{{ _("Urkunde") }}</th>
                                                    <th id="all-charter-title-column" scope="col">{{ _("Datum") }}</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ROWS_HERE
                                            </tbody>
                                        </table>
                                        <button data-target="allCharterGroupTableGROUP_HERE" class="btn btn-primary charter-select-button" type="button" aria-expanded="true" disabled>{{ _('Gewählte Urkunken lesen') }}</button>
                                    </div>
                                </div>"""

all_group_row_template = """
                                        <tr>
                                            <td><input class="charter-part-checkbox" name="URN_HERE-checkbox" type="checkbox" value="URN_HERE"></td>
                                            <td>TITLE_HERE</td>
                                            <td>DATE_HERE</td>
                                        </tr>"""

st_gallen_group_html_template = """
                    <div class="card">
                        <h3 class="card-header" id="part-StGallengruppen">
                            <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#stGallenGroupAccordion" aria-expanded="true" aria-controls="part-collapse-StGallengruppen">
                            <h4>Gruppen der St. Galler Urkunden</h4>
                            </button>
                        </h3>
                        <div class="accordion collapse" id="stGallenGroupAccordion">
                        SUB_GROUP_HERE
                        </div>
                    </div>"""

st_gallen_subgroup_html_template = """
                                <h3 class="card-header" id="part-StGallengruppen-GROUP_HERE">
                                    <button class="btn btn-link btn-block text-left" type="button" data-toggle="collapse" data-target="#part-collapse-StGallengruppen-GROUP_HERE" aria-expanded="true" aria-controls="part-collapse-StGallengruppen-GROUP_HERE">
                                    <h5>Gruppe GROUP_TITLE_HERE</h5>
                                    </button>
                                </h3>
                                <div id="part-collapse-StGallengruppen-GROUP_HERE" class="collapse" aria-labelledby="stGallenGroupTableGROUP_HERE" data-parent="#stGallenGroupAccordion">
                                    <div class="card-body">
                                        <table id="stGallenGroupTableGROUP_HERE" class="table table-sm table-hover table-bordered" aria-label="{{ _('St. Galler Urkundengruppe') }} GROUP_TITLE_HERE">
                                            <thead>
                                                <tr>
                                                    <th id="all-charter-checkbox-column" scope="col"></th>
                                                    <th id="all-charter-title-column" scope="col">{{ _("Urkunde") }}</th>
                                                    <th id="all-charter-title-column" scope="col">{{ _("Datum") }}</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ROWS_HERE
                                            </tbody>
                                        </table>
                                        <button data-target="stGallenGroupTableGROUP_HERE" class="btn btn-primary charter-select-button" type="button" aria-expanded="true">{{ _('Ausgewählte Urkunken anschauen') }}</button>
                                    </div>
                                </div>"""

part_group_row_template = """
                                        <tr>
                                            <td><input class="charter-part-checkbox" name="PART_HERE" type="checkbox" value="URN_HERE"></td>
                                            <td>TITLE_HERE</td>
                                            <td>TEXT_HERE</td>
                                        </tr>"""

for file in files:
    xml = etree.parse(file)
    title = xml.xpath('/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title/text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    urn = xml.xpath('/tei:TEI/tei:text/tei:body/tei:div/@n', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    date_string = xml.xpath('/tei:TEI/tei:text/tei:front/tei:dateline//text()', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    date_elements = xml.xpath('/tei:TEI/tei:text/tei:front/tei:dateline/tei:date', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'})
    date_list = list()
    for element in date_elements:
        if element.get('when'):
            date_list.append(element.get('when'))
        if element.get('notBefore'):
            date_list.append(element.get('notBefore'))
        if element.get('notAfter'):
            date_list.append(element.get('notAfter'))
    if date_list:
        tpq = sorted(date_list)[0]
        taq = sorted(date_list)[-1]
    else:
        tpq = ''
        taq = ''
    title_dict[urn[0]] = {'title': title[0], 'tpq': tpq, 'taq': taq, 'date_string': date_string[0] if date_string else ''}
    for s in xml.xpath('//tei:seg[@function]', namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}):
        part = s.get('function')
        text = ''.join(s.xpath('.//text()'))
        if urn[0] in parts_dict[part]:
            parts_dict[part][urn[0]]['text'].append(text)
        else:
            parts_dict[part][urn[0]] = {'text': [text]}


for good_part in good_parts.keys():
    part_template = copy(html_template)
    part_template = part_template.replace('TITLE_PART_HERE', good_parts[good_part].get('title', good_part))
    part_template = part_template.replace('FORMAT_PART_HERE', good_parts[good_part].get('part_name', good_part))
    part_template = part_template.replace('PART_HERE', good_part)
    all_rows = list()
    for k, v in sorted(parts_dict[good_part].items()):
        single_row = copy(row_template)
        charter_type = type_dict.get(k, '')
        if isinstance(charter_type, list):
            charter_type = '/'.join(charter_type)
        single_row = single_row.replace('URN_HERE', k).replace('PART_HERE', good_part).replace('TEXT_HERE', ' [...] '.join(v['text'])).replace('TITLE_HERE', title_dict[k]['title']).replace('ART_HERE', charter_type).replace('DATE_HERE', title_dict[k]['date_string'])
        all_rows.append(single_row)
    all_part_template.append(part_template.replace('ROWS_HERE', ''.join(all_rows)))

def sort_st_gallen(x):
    num = re.match(r'\d+', x[0])
    try:
        return '{:02}'.format(int(num[0]))
    except:
        return x[0]

def sort_roman_groups(x):
    if 'Total' in x:
        return (1000, 'Z')
    roman_parts = re.match(r'([IVX]+)([a-z]?)', x[0])
    return (roman.fromRoman(roman_parts[1]), roman_parts[2])


for k, v in sorted(charter_group_dict.items(), key=sort_st_gallen):
    group_template = copy(all_group_html_template)
    group_template = group_template.replace('MAIN_GROUP_HERE', '{{ _("Gruppen ähnlicher ") }}' + k.replace('Formen', '{{ _("Urkunden") }}'))
    group_template = group_template.replace('NO_SPACE_GROUP_HERE', k.replace(' ', '_').replace('.', ''))
    group_list = list()
    for sub_group, charters in sorted(v.items(), key=sort_roman_groups):
        all_dates = list()
        if sub_group == 'Total':
            continue
        part_template = copy(all_subgroup_html_template)
        part_template = part_template.replace('GROUP_TITLE_HERE', '{{ _("Gruppe") }} ' + sub_group + ' (' + str(len(charters)) + ' {{ _("von") }} ' + str(v['Total']) + ' {{ _("Urkunden in der Sammlung") }})')
        part_template = part_template.replace('COLLECTION_HERE', '{{ _("Tabelle") }}: ' + k + ' ')
        part_template = part_template.replace('NO_SPACE_GROUP_HERE', k.replace(' ', '_').replace('.', ''))
        part_template = part_template.replace('GROUP_HERE', k.replace(' ', '_').replace('.', '') + sub_group.replace(' ', '_'))
        all_rows = list()
        for charter in sorted(charters):
            if title_dict[charter]['taq']:
                all_dates.append(title_dict[charter]['taq'])
            if title_dict[charter]['tpq']:
                all_dates.append(title_dict[charter]['tpq'])
            single_row = copy(all_group_row_template)
            single_row = single_row.replace('URN_HERE', charter).replace('TITLE_HERE', title_dict[charter]['title']).replace('GROUP_HERE', k).replace('DATE_HERE', title_dict[charter]['date_string'])
            all_rows.append(single_row)
        part_template = part_template.replace('DATE_RANGE_HERE', ' [' + sorted(all_dates)[0].lstrip('0').split('-')[0] + '-' + sorted(all_dates)[-1].lstrip('0').split('-')[0] + ']')
        group_list.append(part_template.replace('ROWS_HERE', ''.join(all_rows)))
    all_charter_groups_list.append(group_template.replace('SUB_GROUP_HERE', ''.join(group_list)))

arengenlist = list()
for sub_group, charters in sorted(arengenfamilien_dict.items(), key=sort_st_gallen):
    if len(charters) == 1:
        continue
    all_dates = list()
    part_template = copy(all_subgroup_html_template)
    part_template = part_template.replace('GROUP_TITLE_HERE', '{{ _("Gruppe") }} ' + sub_group + ' (' + str(len(charters)) + ' {{ _("Texte") }})')
    part_template = part_template.replace('COLLECTION_HERE', '{{ _("Tabelle") }}: ' + 'Arengenfamilien ')
    part_template = part_template.replace('NO_SPACE_GROUP_HERE', 'arengenfamilien')
    part_template = part_template.replace('GROUP_HERE', 'arengenfamilien' + sub_group.replace(' ', '_'))
    all_rows = list()
    for charter in sorted(charters):
        if charter not in title_dict:
            print(charter + ' not found')
            continue
        if title_dict[charter]['taq']:
            all_dates.append(title_dict[charter]['taq'])
        if title_dict[charter]['tpq']:
            all_dates.append(title_dict[charter]['tpq'])
        single_row = copy(all_group_row_template)
        single_row = single_row.replace('URN_HERE', charter).replace('TITLE_HERE', title_dict[charter]['title']).replace('GROUP_HERE', 'Arengenfamilien').replace('DATE_HERE', title_dict[charter]['date_string'])
        all_rows.append(single_row)
    if all_dates:
        part_template = part_template.replace('DATE_RANGE_HERE', ' [' + sorted(all_dates)[0].lstrip('0').split('-')[0] + '-' + sorted(all_dates)[-1].lstrip('0').split('-')[0] + ']')
    else:
        part_template = part_template.replace('DATE_RANGE_HERE', '')
    arengenlist.append(part_template.replace('ROWS_HERE', ''.join(all_rows)))
group_template = copy(all_group_html_template)
group_template = group_template.replace('MAIN_GROUP_HERE', '{{ _("Gruppen ähnlicher ") }}' + '{{ _("Arengen") }}')
group_template = group_template.replace('NO_SPACE_GROUP_HERE', 'arengenfamilien')
charter_parts_list.append(group_template.replace('SUB_GROUP_HERE', ''.join(arengenlist)))

ueberleitungsformel_list = list()
for sub_group, charters in sorted(ueberleitungsformelfamilien_dict.items(), key=sort_st_gallen):
    if len(charters) == 1:
        continue
    all_dates = list()
    part_template = copy(all_subgroup_html_template)
    part_template = part_template.replace('GROUP_TITLE_HERE', '{{ _("Gruppe") }} ' + sub_group + ' (' + str(len(charters)) + ' {{ _("Texte") }})')
    part_template = part_template.replace('COLLECTION_HERE', '{{ _("Tabelle") }}: ' + 'Überleitungsformelfamilien ')
    part_template = part_template.replace('NO_SPACE_GROUP_HERE', 'ueberleitungsformelfamilien')
    part_template = part_template.replace('GROUP_HERE', 'ueberleitungsformelfamilien' + sub_group.replace(' ', '_'))
    all_rows = list()
    for charter in sorted(charters):
        if charter not in title_dict:
            print(charter + ' not found')
            continue
        if title_dict[charter]['taq']:
            all_dates.append(title_dict[charter]['taq'])
        if title_dict[charter]['tpq']:
            all_dates.append(title_dict[charter]['tpq'])
        single_row = copy(all_group_row_template)
        single_row = single_row.replace('URN_HERE', charter).replace('TITLE_HERE', title_dict[charter]['title']).replace('GROUP_HERE', 'Überleitungsformelfamilien').replace('DATE_HERE', title_dict[charter]['date_string'])
        all_rows.append(single_row)
    if all_dates:
        part_template = part_template.replace('DATE_RANGE_HERE', ' [' + sorted(all_dates)[0].lstrip('0').split('-')[0] + '-' + sorted(all_dates)[-1].lstrip('0').split('-')[0] + ']')
    else:
        part_template = part_template.replace('DATE_RANGE_HERE', '')
    ueberleitungsformel_list.append(part_template.replace('ROWS_HERE', ''.join(all_rows)))
group_template = copy(all_group_html_template)
group_template = group_template.replace('MAIN_GROUP_HERE', '{{ _("Gruppen ähnlicher ") }}' + '{{ _("Überleitungsformel") }}')
group_template = group_template.replace('NO_SPACE_GROUP_HERE', 'ueberleitungsformelfamilien')
charter_parts_list.append(group_template.replace('SUB_GROUP_HERE', ''.join(ueberleitungsformel_list)))

formel_zu_formel_tabelle = list()
for k, v in formel_zu_formel_dict.items():
    existing_titles = ['<td>{}</td>'.format(title_dict[x]['title']) for x in v if x.startswith('urn:cts')]
    existing_docs = [x for x in v if x.startswith('urn:cts')]
    existing_refs = ['all' for x in v if x.startswith('urn:cts')]
    if len(existing_docs) > 1:
        formel_zu_formel_tabelle.append("""<tr><td><a class="internal-link" href="{{ url_for('InstanceNemo.r_multipassage', objectIds='""" + '+'.join(existing_docs) + """', subreferences='""" + '+'.join(existing_refs) + """') }}">""" + k + "</a></td>" + ''.join(existing_titles) + "</tr>")
formel_zu_formel_html = """<table id="formel_zu_formel_tabelle" class="table table-sm table-hover table-bordered" aria-label="{{ _('Formel zu Formel Entsprechungen') }}"><thead><tr><th scope="col">{{ _('Gruppennr.') }}</th></tr></thead><tbody>""" + ''.join(formel_zu_formel_tabelle) + '</tbody></table>'

formel_zu_urkunden_tabelle = list()
for k, v in formel_zu_urkunden_dict.items():
    existing_titles = ['<td>{}</td>'.format(title_dict[x]['title']) for x in v if x.startswith('urn:cts')]
    existing_docs = [x for x in v if x.startswith('urn:cts')]
    existing_refs = ['all' for x in v if x.startswith('urn:cts')]
    if len(existing_docs) > 1:
        formel_zu_urkunden_tabelle.append("""<tr><td><a class="internal-link" href="{{ url_for('InstanceNemo.r_multipassage', objectIds='""" + '+'.join(existing_docs) + """', subreferences='""" + '+'.join(existing_refs) + """') }}">""" + k + "</a></td>" + ''.join(existing_titles) + "</tr>")
formel_zu_urkunden_html = """<table id="formel_zu_urkunde_tabelle" class="table table-sm table-hover table-bordered" aria-label="{{ _('Formel zu Urkunde Entsprechungen') }}"><thead><tr><th scope="col">{{ _('Gruppennr.') }}</th></tr></thead><tbody>""" + ''.join(formel_zu_urkunden_tabelle) + '</tbody></table>'

with open('/home/matt/formulae-capitains-nemo/templates/main/all_parts_table.html', mode='w') as f:
    f.write(''.join(all_part_template))

with open('/home/matt/formulae-capitains-nemo/templates/main/charter_group_table.html', mode='w') as f:
    f.write(''.join(all_charter_groups_list))

with open('/home/matt/formulae-capitains-nemo/templates/main/charter_parts_table.html', mode='w') as f:
    f.write(''.join(charter_parts_list))

with open('/home/matt/formulae-capitains-nemo/templates/main/formulae_formulae_table.html', mode='w') as f:
    f.write(formel_zu_formel_html)

with open('/home/matt/formulae-capitains-nemo/templates/main/formulae_charter_table.html', mode='w') as f:
    f.write(formel_zu_urkunden_html)
