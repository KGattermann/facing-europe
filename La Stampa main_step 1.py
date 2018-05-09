#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 10 19:09:52 2017

@author: katia
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 19:40:29 2017

@author: manon
"""

import json
import re, sys, unicodedata
from os import listdir, walk
from os.path import isfile, join, splitext
import glob
import argparse
from collections import defaultdict, OrderedDict
import os
import datetime
import csv
import re
import pandas


VERSIONSTRING="datamanager 0.11"
USERSTRING="katia"


MAAND={"January":1, "gennaio": 1, "February":2, "febbraio":2,"March":3,"marzo":3,
"April":4, "aprile":4, "maggio":5, "May":5, "June":6,"giugno":6, "July":7, "luglio":7,
"agosto": 8, "August":8,"settembre":9,"September":9, "ottobre":10,"October":10,
"November":11,"novembre":11,"December":12,"dicembre":12}

# hier wordt de functie voor het vervangen van leestekens gedefinieerd. Ze worden ERUIT gehaald, niet vervangen door spaties, en dat is juist wat we willen: willem-alexander --> willemalexander
tbl = dict.fromkeys(i for i in range(sys.maxunicode) if unicodedata.category(chr(i)).startswith('P'))


def remove_punctuation(text):
    return text.replace("`","").replace("´","").translate(tbl)


def insert_lexisnexis(pathwithlnfiles,outputfilename):
    """
    Usage: insert_lexisnexis(pathwithlnfiles,recursive)
    pathwithlnfiles = path to a directory where lexis nexis output is stored
    recursive: TRUE = search recursively all subdirectories, but include only files ending on .txt
               FALSE = take ALL files from directory supplied, but do not include subdirectories
    """
    fo = open(outputfilename,mode = "w")
    writer = csv.writer(fo,delimiter=";") # mit \t ist ein tab statt einem Komma zwischen den Variablen
    writer.writerow(["year","month","day", "article", "title", "section", "length", "journal", "suspicious"])  #TODO: HEADERS RICHTIG DEFINIEREN
    
    tekst = {}
    title ={}
    byline = {}
    section = {}
    length = {}
    highlight = {}
    loaddate = {}
    language = {}
    pubtype = {}
    journal = {}
    journal2={}
    pubdate_day = {}
    pubdate_month = {}
    pubdate_year = {}
    pubdate_dayofweek = {}


    alleinputbestanden = glob.glob(pathwithlnfiles)
    artikel = 0
    for bestand in alleinputbestanden:
        print("Now processing", bestand)
        with open(bestand, "r", encoding="utf-8", errors="replace") as f:
            i = 0
            for line in f:
                i = i + 1
                # print "Regel",i,": ", line
                line = line.replace("\r", " ")
                if line == "\n":
                    continue
                matchObj = re.match(r"\s+(\d+) of (\d+) DOCUMENTS", line)
                matchObj2 = re.match(r"\s+(\d{1,2}) (gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre) (\d{4}) (lunedì|martedì|mercoledì|giovedì|venerdì|sabato|domenica)", line)
                matchObj3 = re.match(r"\s+(January|February|March|April|May|June|July|August|September|October|November|December) (\d{1,2}), (\d{4})", line)
                matchObj4 = re.match(r"\s+(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4}) (Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)", line)
                if matchObj:
                    artikel += 1
                    istitle=True #to make sure that text before mentioning of SECTION is regarded as title, not as body
                    firstdate=True # flag to make sure that only the first time a date is mentioned it is regarded as _the_ date
                    tekst[artikel] = ""
                    title[artikel] = ""
                    while True:
                        nextline=next(f)
                        if nextline.strip()!="":
                            journal2[artikel]=nextline.strip()
                            break
                    continue
                if line.startswith("BYLINE"):
                    byline[artikel] = line.replace("BYLINE: ", "").rstrip("\n")
                elif line.startswith("SECTION"):
                    section[artikel] = line.replace("SECTION: ", "").rstrip("\n")
                elif line.startswith("LENGTH"):
                    istitle=False # everything that follows will be main text rather than title if no other keyword is mentioned
                    length[artikel] = line.replace("LENGTH: ", "").rstrip("\n").rstrip(" woorden")
                elif line.startswith("HIGHLIGHT"):
                    highlight[artikel] = line.replace("HIGHLIGHT: ", "").rstrip("\n")
                elif line.startswith("LOAD-DATE"):
                    loaddate[artikel] = line.replace("LOAD-DATE: ", "").rstrip("\n")
                elif matchObj2 and firstdate==True:
                    # print matchObj2.string
                    pubdate_day[artikel]=matchObj2.group(1)
                    pubdate_month[artikel]=str(MAAND[matchObj2.group(2)])
                    pubdate_year[artikel]=matchObj2.group(3)
                    pubdate_dayofweek[artikel]=matchObj2.group(4)
                    firstdate=False
                elif matchObj3 and firstdate==True:
                    pubdate_day[artikel]=matchObj3.group(2)
                    pubdate_month[artikel]=str(MAAND[matchObj3.group(1)])
                    pubdate_year[artikel]=matchObj3.group(3)
                    pubdate_dayofweek[artikel]="NA"
                    firstdate=False
                elif matchObj4 and firstdate==True:
                    pubdate_day[artikel]=matchObj4.group(1)
                    pubdate_month[artikel]=str(MAAND[matchObj4.group(2)])
                    pubdate_year[artikel]=matchObj4.group(3)
                    pubdate_dayofweek[artikel]=matchObj4.group(4)
                    firstdate=False
                elif (matchObj2 or matchObj3 or matchObj4) and firstdate==False:
                    # if there is a line starting with a date later in the article, treat it as normal text
                    tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
                elif line.startswith("LANGUAGE"):
                    language[artikel] = line.replace("LANGUAGE: ", "").rstrip("\n")
                elif line.startswith("PUBLICATION-TYPE"):
                    pubtype[artikel] = line.replace("PUBLICATION-TYPE: ", "").rstrip("\n")
                elif line.startswith("JOURNAL-CODE"):
                    journal[artikel] = line.replace("JOURNAL-CODE: ", "").rstrip("\n")
                elif line.lstrip().startswith("Copyright ") or line.lstrip().startswith("All Rights Reserved"):
                    pass
                else:
                    if istitle:
                        title[artikel] = title[artikel] + " " + line.rstrip("\n")
                    else:
                        tekst[artikel] = tekst[artikel] + " " + line.rstrip("\n")
    print("Done!", artikel, "articles added.")

    if not len(journal) == len(journal2) == len(loaddate) == len(section) == len(language) == len(byline) == len(length) == len(tekst) == len(pubdate_year) == len(pubdate_dayofweek) ==len(pubdate_day) ==len(pubdate_month):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("Ooooops! Not all articles seem to have data for each field. These are the numbers of fields that where correctly coded (and, of course, they should be equal to the number of articles, which they aren't in all cases.")
        print("journal", len(journal))
        print("journal2", len(journal2))
        print("loaddate", len(loaddate))
        print("pubdate_day",len(pubdate_day))
        print("pubdate_month",len(pubdate_month))
        print("pubdate_year",len(pubdate_year))
        print("pubdate_dayofweek",len(pubdate_dayofweek))
        print("section", len(section))
        print("language", len(language))
        print("byline", len(byline))
        print("length", len(length))
        print("tekst", len(tekst))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!")
        print()
        print("Anyhow, we're gonna proceed and set those invalid fields to 'NA'. However, you should be aware of this when analyzing your data!")


    else:
        print("No missing values encountered.")

    suspicious=0
    for i in range(artikel):
        try:
            art_source = journal[i + 1]
        except:
            art_source = ""
        try:
            art_source2 = journal2[i + 1]
        except:
            art_source2 = ""

        try:
            art_loaddate = loaddate[i + 1]
        except:
            art_loaddate = ""
        try:
            art_pubdate_day = pubdate_day[i + 1]
        except:
            art_pubdate_day = "1"
        try:
            art_pubdate_month = pubdate_month[i + 1]
        except:
            art_pubdate_month = "1"
        try:
            art_pubdate_year = pubdate_year[i + 1]
        except:
            art_pubdate_year = "1900"
        try:
            art_pubdate_dayofweek = pubdate_dayofweek[i + 1]
        except:
            art_pubdate_dayofweek = ""
        try:
            art_section = section[i + 1]
        except:
            art_section = ""
        try:
            art_language = language[i + 1]
        except:
            art_language = ""
        try:
            art_length = length[i + 1]
        except:
            art_length = ""
        try:
            art_text = tekst[i + 1]
        except:
            art_text = ""
        try:
            tone=sentiment(art_text)
            art_polarity=str(tone[0])
            art_subjectivity=str(tone[1])
        except:
            art_polarity=""
            art_subjectivity=""
        try:
            art_byline = byline[i + 1]
        except:
            art_byline = ""

        try:
            art_title = title[i + 1]
        except:
            art_title = ""

        # here, we are going to add an extra field for texts that probably are no "real" articles
        # first criterion: stock exchange notacions and similiar lists:
        ii=0
        jj=0
        for token in art_text.replace(",","").replace(".","").split():
            ii+=1
            if token.isdigit():
                jj+=1
        # if more than 16% of the tokens are numbers, then suspicious = True.
        art_suspicious = jj > .16 * ii
        if art_suspicious: suspicious+=1

        art = {
               "title":art_title,
               "source":art_source2.lower(),
               "text":art_text,
               "section":art_section.lower(),
               "byline":art_byline,
               "datum":datetime.datetime(int(art_pubdate_year),int(art_pubdate_month),int(art_pubdate_day)),
               "length_char":len(art_text),
               "length_words":len(art_text.split()),
               "addedby":VERSIONSTRING,
            "addedbydate":datetime.datetime.now(),
            "addedbyuser":USERSTRING
               }


        writer.writerow([int(art_pubdate_year), int(art_pubdate_month), int(art_pubdate_day), art_text, art_title, art_section, art_length, art_source, int(art_suspicious)])
        #artnoemptykeys={k: v for k, v in art.items() if v}

        #article_id = collection.insert(artnoemptykeys)


    print('\nInserted',len(tekst),"articles, out of which",suspicious,"might not be real articles, but, e.g., lists of stock shares. ") # this is for articles which have too many numbers in there



def main():
    insert_lexisnexis('/home/katia/Documents/Python/Data/*.TXT_short','LaStampa.csv') # note it proceeds from same folder as this py file
    

if __name__ == "__main__":
    main()