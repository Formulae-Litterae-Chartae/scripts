from lxml.builder import ElementMaker
from lxml import etree
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode
import sys
import re
from os import environ

home_dir = environ.get('HOME', '')
bib_source = sys.argv[1] if len(sys.argv) > 1 else home_dir + '/results/formulae_bibliographie.bib'

with open(bib_source) as f:
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(f, parser=parser)

E = ElementMaker(namespace="http://www.tei-c.org/ns/1.0", nsmap={None: "http://www.tei-c.org/ns/1.0"})
entries = E.listBibl()

unicode_mapping_dict = {'Á': 'A',
                         'á': 'a',
                         'À': 'A',
                         'à': 'a',
                         'Â': 'A',
                         'â': 'a',
                         'É': 'E',
                         'é': 'e',
                         'È': 'E',
                         'è': 'e',
                         'Ê': 'E',
                         'ê': 'e',
                         'Í': 'I',
                         'í': 'i',
                         'Ì': 'I',
                         'ì': 'i',
                         'Î': 'I',
                         'î': 'i',
                         'Ó': 'O',
                         'ó': 'o',
                         'Ò': 'O',
                         'ò': 'o',
                         'Ô': 'O',
                         'ô': 'o',
                         'Ú': 'U',
                         'ú': 'u',
                         'Ù': 'U',
                         'ù': 'u',
                         'Û': 'U',
                         'û': 'u',
                         'Ç': 'C',
                         'ç': 'c',
                         'Ŏ': 'O',
                         'ŏ': 'o'}

def sub_ascii(obj):
    return unicode_mapping_dict.get(obj[0], obj[0])

def author_year_sort(record):
    sorter = []
    if 'author' in record:
        sorter.append(re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, record['author']).lower())
    elif 'editor' in record:
        sorter.append(re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, record['editor']).lower())
    else:
        sorter.append(re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, record['title']).lower())
    sorter.append(record['year'] if 'year' in record else '')
    return sorter

old_sort_letter = ""

for e in sorted(bib_database.entries, key=author_year_sort):
    entry = E.biblStruct({'type': e['ENTRYTYPE']})
    author = ''
    new_sort_letter = ''
    if 'author' in e:
        author = []
        for i, a in enumerate(e['author'].split(' and ')):
            if len(a.split(',')) > 1:
                author.append(E.author(E.forename(a.split(',')[-1].strip()), E.surname(a.split(',')[0])))
                if i == 0:
                    new_sort_letter = re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, a.split(',')[0][0]).upper()
            else:
                author.append(E.author(a))
                if i == 0:
                    new_sort_letter = re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, a[0]).upper()
    if 'title' in e:
        title = E.title(e['title'].replace(r'\textquotedbl', '"'))
    else:
        try:
            title = E.title(e['booktitle'].replace(r'\textquotedbl', '"'))
        except KeyError:
            print('No title or booktitle:', e)
            continue
    kurztitel = E.title()
    if 'kurztitel' in e:
        kurztitel = E.title(e['kurztitel'].replace(r'\textquotedbl', '"'), {'type': 'short'})
    elif 'shorttitle' in e:
        kurztitel = E.title(e['shorttitle'].replace(r'\textquotedbl', '"'), {'type': 'short'})
    publisher = E.publisher(e['publisher']) if 'publisher' in e else ''
    edition = E.edition(e['edition']) if 'edition' in e else ''
    pubPlace = E.pubPlace(e['address']) if 'address' in e else ''
    pubDate = E.date(e['year'], {'type': 'publicationDate'}) if 'year' in e else ''
    volume = E.biblScope(e['volume'], {'unit': 'volume'}) if 'volume' in e else ''
    series = ''
    if 'series' in e:
        series = E.series(E.title(e['series'].replace(r'\textquotedbl', '"'), {'level': 's'}), volume)
    editor = ''
    if 'editor' in e:
        editor = []
        for i, ed in enumerate(e['editor'].split(' and ')):
            if len(ed.split(',')) > 1:
                editor.append(E.editor(E.forename(ed.split(',')[-1].strip()), E.surname(ed.split(',')[0])))
                if i == 0 and new_sort_letter == '':
                    new_sort_letter = re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, ed.split(',')[0][0]).upper()
            else:
                editor.append(E.editor(ed))
                if i == 0 and new_sort_letter == '':
                    new_sort_letter = re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, ed[0]).upper()
    unit = 'page'
    if 'notizen' in e and 'Spalten' in e['notizen']:
        unit = 'column'
    pages = E.biblScope(e['pages'], {'unit': unit, 'from': e['pages'].split('-')[0].lstrip(' Ss'), 'to': e['pages'].split('-')[-1].lstrip(' Ss')}) if 'pages' in e else ''
    url = E.ref(e['url'], {'type': 'url'}) if 'url' in e else ''
    urldate = E.date(e['urldate'], {'type': 'urldate'}) if 'urldate' in e else ''
    imprint = E.imprint(pubPlace, publisher, pubDate, urldate)
    if e['ENTRYTYPE'] == 'book':
        # monogr = E.monogr(author, title, edition, imprint)
        monogr = E.monogr()
        for a in author:
            monogr.append(a)
        for ed in editor:
            monogr.append(ed)
        monogr.append(title)
        monogr.append(kurztitel)
        if edition != '':
            monogr.append(edition)
        monogr.append(imprint)
        entry = E.biblStruct(monogr, series, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] in ['incollection', 'inproceedings']:
        analytic = E.analytic() #author, title)
        for a in author:
            analytic.append(a)
        analytic.append(title)
        analytic.append(kurztitel)
        monogr = E.monogr(E.title(e['booktitle'].replace(r'\textquotedbl', '"'), {'level': 'm'})) #, editor, imprint, pages)
        for ed in editor:
            monogr.append(ed)
        monogr.append(imprint)
        if pages != '':
            monogr.append(pages)
        if volume != '':
            monogr.append(volume)
        entry = E.biblStruct(analytic, monogr, series, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] == 'article':
        analytic = E.analytic() #author, title)
        for a in author:
            analytic.append(a)
        analytic.append(title)
        analytic.append(kurztitel)
        try:
            monogr = E.monogr(E.title(e['journal'].replace(r'\textquotedbl', '"'), {'level': 'j'}), imprint, volume, pages)
        except:
            print(e)
        entry = E.biblStruct(analytic, monogr, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] in ['misc', 'techreport']:
        analytic = E.analytic() #author, title)
        for a in author:
            analytic.append(a)
        analytic.append(title)
        analytic.append(kurztitel)
        monogr = E.monogr(imprint)
        if 'url' in e and 'urn:cts:formulae:' in e['url']:
            entry = E.biblStruct(analytic, monogr, url, {'type': 'formula'})
        else:
            entry = E.biblStruct(analytic, monogr, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] == 'phdthesis':
        school = '' #E.publisher(E.orgName(e['type'].replace('Zugleich: ', '').replace('Zugl.: ', ''), {'type': 'school'}))
        publisher = E.publisher(e['school'])
        imprint = E.imprint(pubPlace, publisher, pubDate, school, urldate)
        monogr = E.monogr() #author, title, edition, imprint)
        for a in author:
            monogr.append(a)
        monogr.append(title)
        monogr.append(kurztitel)
        if edition != '':
            monogr.append(edition)
        monogr.append(imprint)
        entry = E.biblStruct(monogr, series, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] == 'unpublished':
        analytic = E.analytic()
        for a in author:
            analytic.append(a)
        analytic.append(title)
        analytic.append(kurztitel)
        monogr = E.monogr(imprint)
        entry = E.biblStruct(analytic, monogr, url, {'type': e['ENTRYTYPE']})
    if new_sort_letter == '':
        new_sort_letter = re.sub(r'[ÁáÀàÂâÉéÈèÊêÍíÌìÎîÓóÒòÔôÚúÙùÛûÇçŎŏ]', sub_ascii, title.xpath('.//text()')[0][0]).upper()
    if re.fullmatch(r'\d', new_sort_letter):
        new_sort_letter = 'nr'
    if new_sort_letter != old_sort_letter:
        entry.set('{http://www.w3.org/XML/1998/namespace}id', 'BL-' + new_sort_letter)
    old_sort_letter = new_sort_letter
    entries.append(entry)
    

tree = etree.parse(home_dir + '/scripts/internal/biblatex/tei_bibliography_template.xml')
tree.xpath('//tei:body', namespaces={'tei': "http://www.tei-c.org/ns/1.0"})[0].append(entries)
xml_str = etree.tostring(tree, pretty_print=True, encoding="unicode")
xml_str = xml_str.replace('><', '>\n<')
with open(bib_source.replace('.bib', '.xml'), mode="w") as f:
    f.write(xml_str)
