#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 19:10:26 2017

@author: katia
"""

#converting csv file to dataframe
import pandas as pd
df_LaStampa = pd.read_csv('/home/katia/Documents/Python/Data/LaStampa.csv', sep=None) 


df_LaStampa = df_LaStampa[pandas.notnull(df_LaStampa['article'])]

#converting dataframe to dictionary
LaStampa_dict = df_LaStampa.to_dict(orient='dict')


#_____________________Commission members articles____________________

# importing and creating a string of commissioners
with open("/home/katia/Documents/Python/Data/list_commissioners_IT.txt", "r") as commissioners:
    commissioners=commissioners.read()

# creating commissioner list of the string
commissioners_list=commissioners.split()
del commissioners

#creating list of VK articles in dict
art_text=LaStampa_dict["article"]
articles=list(art_text.values()) 

# returns a csv with article, Commissionmembers & Commissionmembercounts as variables
from collections import defaultdict
results = defaultdict(list)

import re
for element in commissioners_list:
    for article in articles:
        list_namecounts = len(re.findall(element, article))     
        results[element].append(list_namecounts)


#write dictionary to pandaframe
df_commissionmembers=pd.DataFrame(results)
pd.DataFrame(results)
article2df = pd.Series(articles)
df_commissionmembers['article'] = article2df.values

# merging both data frames by article
df_LS_articles_commission=pd.merge(df_LaStampa, df_commissionmembers, on='article')
df_LS_articles_commission.to_csv('LS_articles_commission.csv')

#deleting all unnecessary elements
del df_LS_articles_commission
del df_commissionmembers
del element
del list_namecounts
del results
del art_text
del article
del articles
del LaStampa_dict