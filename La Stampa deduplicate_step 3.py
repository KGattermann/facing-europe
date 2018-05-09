#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Script to detect duplicates in newspaper dataset
'''


import datetime
import csv
from collections import defaultdict
import sys
import unicodedata
import scipy as sp
import numpy as np
import random

from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer


#%% define variables

STOPWORDS=set(stopwords.words('italian'))
THRESHOLD = .70
DELIMITER = ','


#%% define functions

tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))
def remove_punctuation(text):
    return text.replace("`","").replace("´","").translate(tbl)

#%% read data

comparisons=defaultdict(list)

with open('/home/katia/Documents/Python/Data/LS_articles_commission.csv') as fi:
    reader = csv.reader(fi, delimiter=DELIMITER)
    headers = next(reader)
    for row in reader:
        identifier = row[0]
        tekst = " ".join([w for w in remove_punctuation(row[4]).split() if w not in STOPWORDS])        
        datum = "{}-{}-{}".format(row[1],row[2],row[3])
        comparisons[datum].append((identifier,tekst))

#%% Make BOW-represenmtation of texts using TF-IDF scores

localduplicates=defaultdict(set)

for k,documents in comparisons.items():
    print("Now processing",k)
    tfidf = TfidfVectorizer().fit_transform([item[1] for item in documents])
    pairwise_similarity = tfidf * tfidf.T
    cx = sp.sparse.coo_matrix(pairwise_similarity)
    for i,j,v in zip(cx.row, cx.col, cx.data):
        if v>THRESHOLD and i<j:  # lets iterate only over one half of the matrix, its symmetrical after all
            print(documents[i][0]+'-->'+documents[j][0],':'+str(v))
            #a,b = i,j   
            #if documents[b][0] in localduplicates:
            #    b,a = i,j
            #if documents[a][0] in {e for s in localduplicates.values() for e in s}:
            #    b,a = a,b
            localduplicates[documents[i][0]].add(documents[j][0])
    #print(localduplicates)


#%% save!

markasduplicate = {e for s in localduplicates.values() for e in s}
#markasduplicate -= set(localduplicates.keys())

with open('/home/katia/Documents/Python/Data/LS_articles_commission.csv') as fi, open('/home/katia/Documents/Python/Data/LS_articles_commission_dup.csv',mode='w') as fo:
        reader=csv.reader(fi,delimiter=DELIMITER)
        writer=csv.writer(fo,delimiter=DELIMITER)
        headers = list(next(reader))
        headers.append('duplicate')
        writer.writerow(headers)
        for row in reader:
            row2write = list(row)
            row2write.append(int(row[0] in markasduplicate))
            writer.writerow(row2write)
        