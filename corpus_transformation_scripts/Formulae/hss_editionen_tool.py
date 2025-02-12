import errno
import os
import logging
import argparse

DEFAULT_HSS_EDITIONEN_FILE_NAME='hss_editionen.xml'

# select="document(concat(replace($folderName, '/data/.*', ''), '/hss_editionen.xml'))"
def find_hss_editionen(hss_editionen_file_name=DEFAULT_HSS_EDITIONEN_FILE_NAME):
    if os.path.isfile(hss_editionen_file_name):
        return os.path.join(hss_editionen_file_name)
    else:
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), hss_editionen_file_name)

def check_hss_editionen(hss_editionen_file_name=DEFAULT_HSS_EDITIONEN_FILE_NAME,logging=None):
    return check_for_illegal_strings_in_hss_editionen(find_hss_editionen(),logging)

def check_for_illegal_strings_in_hss_editionen(hss_editionen_file_path, logging=None):
    with open(hss_editionen_file_path) as file:
        content = file.read()
        illegal_strings = ['&lt;xml&gt;', '&lt;/xml&gt;', 'lat001"&gt;', '<b>', '<span', 'span>']
        illegal_strings_found = []
        for illegal_string in illegal_strings:
            if illegal_string in content:
                illegal_strings_found.append(illegal_string)
        if (0 == len(illegal_strings_found)):
            if logging is not None:
                logging.info('No errors detected in {}'.format(hss_editionen_file_path) )
            else:
                print('No errors detected in {}'.format(hss_editionen_file_path) )
        else:
            error_message = '{} found in {}. Please consider to repair it using hss_edition_tool.py --repair'.format(illegal_strings_found, hss_editionen_file_path)
            if logging is not None:
                logging.error(error_message)
            else:
                raise ValueError(errno.ENOENT, os.strerror(errno.ENOENT), error_message)
    return illegal_strings_found



def repair(hss_editionen_file_name=DEFAULT_HSS_EDITIONEN_FILE_NAME, logging=None):
    hss_editionen_file_path = find_hss_editionen(hss_editionen_file_name)
    with open(hss_editionen_file_path, 'r') as read_file: 
        data = read_file.read()
        data = data.replace('<', '&lt;')
        data = data.replace('>', '&gt;')
        data = data.replace('&lt;xml&gt;', '<xml>')
        data = data.replace('&lt;/xml&gt;', '</xml>')
        data = data.replace('lat001"&gt;', 'lat001">')
        data = data.replace('&lt;formula', '<formula')
        data = data.replace('&lt;/formula&gt;,', '</formula>')
    
    with open(hss_editionen_file_path, 'w') as write_file: 
        write_file.write(data)
        if logging is not None:
            logging.error('Successfully repaired {}'.format(hss_editionen_file_path))

check = check_for_illegal_strings_in_hss_editionen

if __name__ == '__main__':
    # Example way to run it:
    # cd formel_transform/output/auvergne/
    # python3 /home/thorben.schomacker/git/scripts/corpus_transformation_scripts/Formulae/hss_editionen_tool.py
    # python3 /home/thorben.schomacker/git/scripts/corpus_transformation_scripts/Formulae/hss_editionen_tool.py -f "/home/thorben.schomacker/git/scripts/formel_transform/output/auvergne/hss_editionen copy 2.xml"
    parser=argparse.ArgumentParser(description="Script to sanity check and repair hss_edition-files.")
    parser.add_argument('-r', '--repair', action='store_true', help='If set the hss_edition-file is repaired.')
    parser.add_argument('-rc', '--repair_check', action='store_true', help='If set the hss_edition-file is repaired and checked afterwards.')
    parser.add_argument('-f', '--file', type=str,default=DEFAULT_HSS_EDITIONEN_FILE_NAME, help='Location of the hss_edition-file')
    parser.add_argument('-l', '--logging_level', type=str, default='INFO', choices=['INFO', 'DEBUG', 'ERROR', 'WARN'], 
                                                help='Logging level of the python logger.')
    args=parser.parse_args()


    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                    encoding='utf-8', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(args.logging_level)

    hss_editionen_file_path = find_hss_editionen(hss_editionen_file_name=args.file)
    check_for_illegal_strings_in_hss_editionen(hss_editionen_file_path, logging)
    if args.repair or args.repair_check:
        repair(hss_editionen_file_name=args.file, logging=logging)
        if args.repair_check:
            check(hss_editionen_file_path, logging=logging)