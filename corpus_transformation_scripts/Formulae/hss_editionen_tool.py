import errno
import os
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                    encoding='utf-8', datefmt='%H:%M:%S')
# TODO: set the level via cl argument
logging.getLogger().setLevel('INFO')

# select="document(concat(replace($folderName, '/data/.*', ''), '/hss_editionen.xml'))"
def find_hss_editionen(hss_editionen_file_name='hss_editionen copy.xml'):
    if os.path.isfile(hss_editionen_file_name):
        return os.path.join(hss_editionen_file_name)
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), hss_editionen_file_name)

def check_hss_editionen():
    return check_for_illegal_strings_in_hss_editionen(find_hss_editionen())

def check_for_illegal_strings_in_hss_editionen(hss_editionen_file_path):
    with open(hss_editionen_file_path) as file:
        content = file.read()
        illegal_strings = ['&lt;xml&gt;', '&lt;/xml&gt;', 'lat001"&gt;', '<b>', '<span', 'span>']
        illegal_strings_found = []
        for illegal_string in illegal_strings:
            if illegal_string in content:
                illegal_strings_found.append(illegal_string)
        if (0 == len(illegal_strings_found)):
            logging.error('No errors detected in {}'.format(hss_editionen_file_path) )
        else:
            logging.error('{} found in {}'.format(illegal_strings_found, hss_editionen_file_path) )
            logging.error('consider to repair this file using hss_edition_tool.py --repair')
    return illegal_strings_found

def repair():
    # Implement these operations in the same order I wrote them down:
    # Replace all < with &lt;
    # Replace all > with &gt;
    # Replace &lt;xml&gt; with <xml>
    # Replace &lt;/xml&gt; with </xml>
    # Replace lat001"&gt; with lat001">
    # Replace &lt;formula with <formula
    # Replace &lt;/formula&gt; with </formula>
    pass

if __name__ == '__main__':
    hss_editionen_file_path = find_hss_editionen()
    check_for_illegal_strings_in_hss_editionen(hss_editionen_file_path)
    if repair_flag:
        repair()