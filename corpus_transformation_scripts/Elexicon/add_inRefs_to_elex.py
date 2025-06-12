from lxml.builder import ElementMaker
from lxml import etree
from glob import glob
import os
import sys
from json import load
import html
import lxml.html


home_dir = os.environ.get('HOME', '')
dest = str(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(home_dir, 'formulae-corpora') 
basedir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(dest, 'formulae_elexicon_mapping.json')) as f:
    form_elex_mapping = load(f)

elex_md_files = glob(os.path.join(dest, 'data/elexicon/*/__capitains__.xml'))

ns = {
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "dct": "http://purl.org/dc/terms/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "cpt": "http://purl.org/capitains/ns/1.0#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "bib": "http://bibliotek-o.org/1.0/ontology/",
    "cts": "http://chs.harvard.edu/xmlns/cts",
    "foaf": "http://xmlns.com/foaf/0.1/"
}

E = ElementMaker(namespace=ns['dct'], nsmap=ns)

def is_valid_escaped_html(text):
    """Validate escaped pseudo-HTML by unescaping and parsing as XML fragment."""
    unescaped = html.unescape(text)
    wrapped = f"<fragment>{unescaped}</fragment>"
    try:
        etree.fromstring(wrapped)
        return True
    except etree.XMLSyntaxError:
        return False

def auto_correct_with_parser(text):
    """
    Auto-correct malformed escaped HTML using lxml.html parser.
    """
    unescaped = html.unescape(text)
    fragment = f"<div>{unescaped}</div>"  # add temporary root
    try:
        doc = lxml.html.fromstring(fragment)
        cleaned = lxml.html.tostring(doc, encoding="unicode", method="html")
        # Remove artificial wrapper again
        cleaned = cleaned.replace("<div>", "").replace("</div>", "").strip()
        # Escape back for XML storage
        return html.escape(cleaned)
    except Exception as e:
        return text  # fallback: return original text if correction failed

for filename in elex_md_files:
    key = filename.split('/')[-2]
    
    if key not in form_elex_mapping:
        continue

    xml = etree.parse(filename)
    changed = False

    for readable in xml.xpath('/cpt:collection/cpt:members/cpt:collection[@readable="true"]', namespaces=ns):
        md = readable.xpath('cpt:structured-metadata', namespaces=ns)[0]

        is_refs = md.xpath('dct:isReferencedBy', namespaces=ns)
        for is_ref in is_refs:
            md.remove(is_ref)

        for ref, cit in form_elex_mapping[key].items():
            new_cit = []
            for c in cit:
                if is_valid_escaped_html(c):
                    new_cit.append(c)
                else:
                    corrected = auto_correct_with_parser(c)
                    if is_valid_escaped_html(corrected):
                        print(f"[WARNING] Auto-corrected citation in file '{filename}':\n  Original: {c}\n  Corrected: {corrected}\n")
                        new_cit.append(corrected)
                        changed = True
                    else:
                        print(
                            f"[ERROR] Could not auto-correct malformed escaped HTML in file '{filename}':\n  URN: {ref}\n  Problematic citation: {c}\n"
                        )

            elem = E.isReferencedBy('%' + ref + '%' + '%'.join(new_cit))
            elem.tail = '\n  '
            md.append(elem)

    if changed:
        xml.write(filename, encoding='utf-8', pretty_print=True)
        print(f"[FIXED] File corrected and saved: {filename}")
    else:
        pass
        #print(f"[OK] File processed successfully: {filename}")
