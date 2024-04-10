import requests
from bs4 import BeautifulSoup
import pandas as pd
import regex as re
import time
from time import mktime
from tqdm import tqdm  #licznik
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from functions import date_change_format_short
import math

#%%

def get_listing_links(url):
    # url = 'https://www.e-enlightenment.com/browse/letters/'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    sections = soup.select('#sectionlist a')
    links = []
    for section in sections:
        # section = sections[7]
        base_link = 'https://www.e-enlightenment.com' + section['href'][:-1]
        subpages = range(1, math.ceil(int(section['title'].split('(')[-1].replace(')','').replace(',',''))/15)+1)
        for subpage in subpages:
            link = base_link + str(subpage)
            links.append(link)
    return links

def get_letter_links(url):
    # url = links[0]
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, "html.parser")
    letters_links_15 = ['https://www.e-enlightenment.com' + e['href'] for e in soup.select('#simple_resultslist a')]
    letters_links.extend(letters_links_15)

def get_dictionary_page(url):
# for url in tqdm(letters_links[6180:6350]):
    # url = letters_links[16605]
    # url = letters_links[letters_links.index(list(all_result.keys())[-1])+1]
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    
    content = soup.find('div', {'id': 'content'}).text
    try:
        decade = re.search('(?<=&s\=)\d+(?=&)', url).group()
        title = soup.find_all('p')[0].text.replace('Title : ', '')
        
        if 'Subtitle : ' in content:
            subtitle = soup.find_all('p')[1].text.replace('Subtitle : ', '')
            date = soup.find_all('p')[2].text.replace('Date : ', '')
            writer = soup.find_all('p')[3].text.replace('Writer : ', '')
            recipient = soup.find_all('p')[4].text.replace('Recipient : ', '').split('\nIncipit : ')[0]
            incipit = soup.find_all('p')[4].text.replace('Recipient : ', '').split('\nIncipit : ')[-1].split('\n DOI')[0].strip()
            doi = soup.find('input', {'type': 'text'})['value']
        else:
            subtitle = None
            date = soup.find_all('p')[1].text.replace('Date : ', '')
            writer = soup.find_all('p')[2].text.replace('Writer : ', '')
            recipient = soup.find_all('p')[3].text.replace('Recipient : ', '').split('\nIncipit : ')[0]
            incipit = soup.find_all('p')[3].text.replace('Recipient : ', '').split('\nIncipit : ')[-1].split('\n DOI')[0].strip()
            doi = soup.find('input', {'type': 'text'})['value']
    
        temp_dict = {'title': title,
                     'subtitle': subtitle,
                     'date': date,
                     'writer': writer,
                     'recipient': recipient,
                     'incipit': incipit,
                     'doi': doi,
                     'decade': decade}
    
    except KeyError:
        temp_dict = None
    
    all_result[url] = temp_dict

#%% main
listing_links = get_listing_links('https://www.e-enlightenment.com/browse/letters/')

letters_links = []
with ThreadPoolExecutor() as excecutor:
    list(tqdm(excecutor.map(get_letter_links, listing_links),total=len(listing_links)))

all_result = {}
with ThreadPoolExecutor() as excecutor:
    list(tqdm(excecutor.map(get_dictionary_page, letters_links),total=len(letters_links)))

# letters_links.index(list(all_result.keys())[-1])+1

all_result_wrong = [k for k,v in all_result.items() if not v]
all_result_ok = {k:v for k,v in all_result.items() if k not in all_result_wrong}

df = pd.DataFrame().from_dict(all_result_ok, orient='index')

with pd.ExcelWriter("data/monita_privata_e-enlightenment.xlsx", engine='xlsxwriter', engine_kwargs={'options': {'strings_to_urls': False}}) as writer:    
    df.to_excel(writer, 'e-enlightenment')





























    