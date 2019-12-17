from glob import glob
from lxml import etree
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sys import argv
import csv
from pandas import DataFrame

vectorizer_dict = {'count': CountVectorizer(), 'tfidf': TfidfVectorizer()}
doc_names = []
texts = []
if argv[3] == 'xml':
    files = glob('/home/matt/results/formulae/search/*{}*.txt'.format(argv[1]))
    for file in sorted(files): 
        xml = etree.parse(file) 
        try: 
            texts.append(xml.xpath('/xml/inflected/text()')[0]) 
        except IndexError: 
            continue 
        doc_names.append(file.split('/')[-1].split('.')[1])
elif argv[3] == 'csv':
    with open(argv[1]) as f:
        csv_data = csv.DictReader(f, delimiter='\t')
        for row in csv_data:
            if row[argv[4]]:
                try:
                    texts.append(row[argv[4]])
                except IndexError:
                    continue
            else:
                continue
            doc_names.append(row['Überlieferung'] + row['Nummer + Seite'])
    
vectorizer = vectorizer_dict[argv[2]]

matrix = vectorizer.fit_transform(texts)
cos_sim = cosine_similarity(matrix)

with open('/home/matt/results/collation/Franziska/cos_sim_{}_{}_{}.csv'.format(argv[2], argv[1].split('/')[-1], argv[4].replace('/', '-')), mode='w') as f: 
    f.write('\t' + '\t'.join(doc_names) + '\n') 
    for i, doc in enumerate(doc_names): 
        f.write(doc + '\t' + '\t'.join(['{:.2}'.format(x) for x in cos_sim[i]]) + '\n')
