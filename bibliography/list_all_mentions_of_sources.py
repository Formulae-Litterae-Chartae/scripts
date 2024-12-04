import logging
import argparse
import os.path
import csv
# python3 -m list_all_mentions_of_sources -s "Formulae Turonenses Additamenta" "Cartae Senonicae" "Cartae Senonicae Appendix"

def retrieve_all_occurrences(corpus_folder: str, sources: list[str]) -> list[str]:
    results = []
    data_folder = os.path.join(corpus_folder,"data")
    for folder in os.listdir(data_folder):
        collection_folder = os.path.join(data_folder,folder)
        for subfolder in os.listdir(collection_folder): 
            formel_folder = os.path.join(collection_folder, subfolder)
            if os.path.isdir(formel_folder):
                for file_name in os.listdir(formel_folder): 
                    file_path = os.path.join(formel_folder,file_name)
                    if os.path.isfile(file_path):
                        with open(file_path,'r') as f:
                            for line in f:
                                for source in sources:
                                    if source+" </bibl>" in line or 'n="'+source+',' in line:
                                        file_name_parts = file_name.split('.')
                                        results.append([source, file_name_parts[0], file_name_parts[1]])
    return results


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description="Script to list all files mentioning a specific sources.")
    parser.add_argument("--corpus_folder","-c", type=str,default='/home/thorben.schomacker/git/formulae-corpora', help='Path to your local copy of https://github.com/Formulae-Litterae-Chartae/formulae-corpora')
    parser.add_argument("--sources","-s", action="extend", nargs="+", type=str, help="One or more sources.", required=True)
    parser.add_argument("--logging_level","-l", type=str, help="Logging level", default="INFO")
    parser.add_argument("--output_file","-o", type=str, help="Location of the output file.", default='results.csv')
    args=parser.parse_args()

    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s - %(message)s', 
                        encoding='utf-8', datefmt='%H:%M:%S')
    logging.getLogger().setLevel(args.logging_level.upper())


    results = retrieve_all_occurrences(args.corpus_folder, args.sources)
    

    csv_file_path = args.output_file
    with open(csv_file_path, 'w+') as myfile:
        wr = csv.writer(myfile)
        wr.writerow(['source', 'collection', 'formel'])
        for result_row in results:
            wr.writerow(result_row)
    logging.info("Written "+str(len(results))+" results to "+csv_file_path)
