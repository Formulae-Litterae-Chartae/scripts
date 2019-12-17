from lxml.builder import ElementMaker
from lxml import etree
import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode


with open('/home/matt/results/Bibliographie_E-Lexikon.bib') as f:
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    bib_database = bibtexparser.load(f, parser=parser)

E = ElementMaker(namespace="http://www.tei-c.org/ns/1.0", nsmap={None: "http://www.tei-c.org/ns/1.0"})
entries = E.listBibl()

def author_year_sort(record):
    sorter = []
    if 'author' in record:
        sorter.append(record['author'])
    elif 'editor' in record:
        sorter.append(record['editor'])
    else:
        sorter.append(record['title'])
    sorter.append(record['year'] if 'year' in record else '')
    return sorter

for e in sorted(bib_database.entries, key=author_year_sort):
    entry = E.biblStruct({'type': e['ENTRYTYPE']})
    author = ''
    if 'author' in e:
        author = []
        for a in e['author'].split(' and '):
            if len(a.split(',')) > 1:
                author.append(E.author(E.forename(a.split(',')[-1].strip()), E.surname(a.split(',')[0])))
            else:
                author.append(E.author(a))
    title = E.title(e['title'].replace(r'\textquotedbl', '"'))
    kurztitel = E.title(e['kurztitel'].replace(r'\textquotedbl', '"'), {'type': 'short'})
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
        for ed in e['editor'].split(' and '):
            if len(ed.split(',')) > 1:
                editor.append(E.editor(E.forename(ed.split(',')[-1].strip()), E.surname(ed.split(',')[0])))
            else:
                editor.append(E.editor(ed))
    unit = 'page'
    if 'notizen' in e and 'Spalten' in e['notizen']:
        unit = 'column'
    pages = E.biblScope(e['pages'], {'unit': unit, 'from': e['pages'].split('-')[0], 'to': e['pages'].split('-')[-1]}) if 'pages' in e else ''
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
    elif e['ENTRYTYPE'] == 'incollection':
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
        monogr = E.monogr(E.title(e['journal'].replace(r'\textquotedbl', '"'), {'level': 'j'}), imprint, volume, pages)
        entry = E.biblStruct(analytic, monogr, url, {'type': e['ENTRYTYPE']})
    elif e['ENTRYTYPE'] == 'misc':
        analytic = E.analytic() #author, title)
        for a in author:
            analytic.append(a)
        analytic.append(title)
        analytic.append(kurztitel)
        monogr = E.monogr(imprint)
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
    entries.append(entry)
    

tree = etree.parse('/home/matt/docx_tei_cte_conversion/internal/biblatex/tei_bibliography_template.xml')
tree.xpath('//tei:body', namespaces={'tei': "http://www.tei-c.org/ns/1.0"})[0].append(entries)
# tree.write('/home/matt/results/Bibliographie_E-Lexikon.xml', encoding="utf-8", pretty_print=True)
xml_str = etree.tostring(tree, pretty_print=True, encoding="unicode")
xml_str = xml_str.replace('><', '>\n<')
with open('/home/matt/results/Bibliographie_E-Lexikon.xml', mode="w") as f:
    f.write(xml_str)
