## DO NOT RUN!!!
##
## This file contains the code used to extract the data for the first time
## to create the csv files for the following countries:
##    - Spain
##    - Italy

## Libraries
from selenium import webdriver
import pandas as pd
import re
import tabula
import ssl
import PyPDF2
import io
import requests
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

###   SPAIN   ##############################################
############################################################
## A daily report in pdf is in the url:
## https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_{no}_COVID-19.pdf
## Where {no} is the report number. First public report is online from 31
## when they found 1 case in La Gomera from 31.01, one from Mallorca, one
## in Tenerife, 2 in Madrid, 1 in Castellon and 1 in Barcelona.
## total of 8 by 26.02.2020. From here only text
## Report No. 35 (3.03.2020) is the first one with a table per province
## and a similar Table for Italy. We can start from here

def Spain_get_table (no):
    """
Extracts data from the report number<no> obtained from the Health 
department of spain (www.mscbs.gob.es).

Returns the data, as extracted, as pd.dataframe
    """
    URL = f"https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Actualizacion_{no}_COVID-19.pdf"
    ## Extract all tables 
    tables = tabula.read_pdf(URL, pages = "all", multiple_tables = True)
    ## Iterate over all tables and find our target table
    for df in tables:
        for col in df:
            if type(df[col][1]) == str:
                bool_list = df[col].str.contains('Asturias')
                for element in bool_list:
                    if element == True:
                        target = df
    ## <target? contains our data
    try:
        target
    except NameError:
        print("Table not found")
        sys.exit(1)
    ## Get timestamp
    r = requests.get(URL, verify=False)
    f = io.BytesIO(r.content)
    reader = PyPDF2.PdfFileReader(f)
    contents = reader.getPage(0).extractText()
    contents = re.sub('\n', '', contents)
    match = re.search(r'\d{2}.\d{2}.\d{4}', contents)
    if match is None:
        match = re.search(r'\d{1}.\d{2}.\d{4}', contents)
    if match is None:
        print("Date not found")
        date = 'NaN'
    else:
        date = datetime.strptime(match.group(), '%d.%m.%Y').date()
    target['Timestamp'] = date
    return(target)

## BUG
spain35 = Spain_get_table(35) # Did not find the table (which exists)

spain36 = Spain_get_table(36)
spain37 = Spain_get_table(37)
spain38 = Spain_get_table(38)
spain39 = Spain_get_table(39)
spain40 = Spain_get_table(40)
spain41 = Spain_get_table(41)
spain42 = Spain_get_table(42)
spain43 = Spain_get_table(43)

spain44 = Spain_get_table(44) # Page not found
spain45 = Spain_get_table(45) # Page not found

spain46 = Spain_get_table(46)
spain47 = Spain_get_table(47)
spain48 = Spain_get_table(48)
## FINAL: make a function to extract the data 

spain_over_time = spain36.append([spain37, spain38, spain39,spain40, spain41, spain42,spain43, spain46, spain47,spain48], ignore_index = True)

list(spain_over_time.columns)

spain = pd.DataFrame({"country":"Spain", "region":spain_over_time["CCAA"], "confirmed_infected":spain_over_time["Total casos"], "dead":spain_over_time["Fallecidos"], "timestamp": spain_over_time["Timestamp"]}) 

#spain.to_csv("Spain_first.csv", index = False)

###   FRANCE   #############################################
############################################################
## The website provided below contains all the data exactly as we need
## We just need to translate it

dat_raw = pd.read_csv("https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv")

list(dat_raw.columns)
dat_raw['granularite']

france = pd.DataFrame({"country":"France", "granularity":dat_raw["granularite"], "name":dat_raw["maille_nom"], "confirmed_infected": dat_raw["cas_confirmes"], "dead": dat_raw["deces"], "recovered": dat_raw["reanimation"], "timestamp": dat_raw["date"]})

#france.to_csv("France_first.csv", index = False)

## Details
## Granularity has several variables, in the order
## World = "monde"
## Country = "pays"
## "departement" and "region": France is divided into 18 regions
##                            (13 metropolitan) and 101 departments 
