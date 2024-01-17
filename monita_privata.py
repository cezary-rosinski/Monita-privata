import bibtexparser
import pandas as pd
import regex as re
import random
import sys
sys.path.insert(1, 'C:/Users/Cezary/Documents/IBL-PAN-Python')
from geonames_accounts import geonames_users
import requests
import time
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

#%%

file = r"C:\Users\Cezary\Downloads\exportlist (1).txt"

with open(file, encoding='utf-8') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

data = bib_database.entries

df = pd.DataFrame(data)


year = set(df['year'].to_list())

[e for e in year if '–' in e]

def set_year(x):
    if x.isnumeric():
        return (int(x), 'certain')
    elif x.replace('[','').replace(']','').isnumeric():
        return (int(x.replace('[','').replace(']','')), 'certain')
    elif re.findall('\d{4}', x) and '?' in x:
        return (int(re.findall('\d{4}', x)[0]), 'uncertain')
    elif '?' in x and re.findall('\d{3}-', x):
        return (int(re.findall('\d{3}-', x)[0].replace('-', '0')), 'uncertain')
    elif all(e in x for e in ['c', '–']):
        return (int(re.findall('\d{4}', x)[0]), 'uncertain')
    elif 'c' in x and re.findall('\d{4}', x):
        return (int(re.findall('\d{4}', x)[0]), 'uncertain')
    elif '–' in x:
        return (int(re.findall('\d{4}', x)[0]), 'certain')
    elif all(e in x for e in ['?', 'XVIII']):
        return (1700, 'uncertain')
    elif 'XVIII' in x:
        return (1700, 'uncertain')
    elif all(e in x for e in ['?', 'XVII']):
        return (1600, 'uncertain')
    elif 'XVII' in x:
        return (1600, 'uncertain')
    elif 'n.d' in x:
        return (0, 'uncertain')
    elif re.findall('\d{4}', x):
        return (int(re.findall('\d{4}', x)[0]), 'uncertain')
    else: return('solution not provided')
    
        
#test poprawności funkcji `set_year`
for e in year:
    if set_year(e) == 'solution not provided':
        print(e)

def set_origin_of_the_year(x):
    if '[' in x:
        return 'external'
    else: return 'internal'
    
def set_privata_in_title(x):
    if 'privata' in x.lower():
        return True
    else: return False

def set_secreta_in_title(x):
    if 'secreta' in x.lower():
        return True
    else: return False   
    
#dopytać RM, jaka informacja i w którym polu
#def set_publishing_form(x):

#address

places = set(df['address'].to_list()) 
# places_with_geonames = {}
    
def query_geonames(m):
    # m = 'Dublin'
    url = 'http://api.geonames.org/searchJSON?'
    params = {'username': random.choice(geonames_users), 'q': m, 'featureClass': 'P', 'style': 'FULL'}
    result = requests.get(url, params=params).json()
    if 'status' in result:
        time.sleep(5)
        query_geonames(m)
    else:
        try:
            geonames_resp = {k:v for k,v in max(result['geonames'], key=lambda x:x['score']).items() if k in ['geonameId', 'name', 'lat', 'lng']}
        except ValueError:
            geonames_resp = None
        places_with_geonames[m] = geonames_resp

places_with_geonames = {}
with ThreadPoolExecutor() as excecutor:
    list(tqdm(excecutor.map(query_geonames, places),total=len(places)))

places_without_geonames = {k:v for k,v in places_with_geonames.items() if not v}
places_with_geonames = {k:v for k,v in places_with_geonames.items() if k not in places_without_geonames}

df = pd.DataFrame().from_dict(places_with_geonames, orient='index').reset_index().rename(columns={'index': 'query'})
        
for m in tqdm(places):
    query_geonames(m)
        
max(lst, key=lambda x:x['price'])        
        
        
        
        
        
        
        
        geonames_resp = [[e['geonameId'], e['name'], e['lat'], e['lng'], [f['name'] for f in e['alternateNames']] if 'alternateNames' in e else []] for e in result['geonames']]
        [e[-1].append(e[1]) for e in geonames_resp]
        if len(geonames_resp) == 0:
            miejscowosci_total[m] = geonames_resp
        if len(geonames_resp) == 1:
            miejscowosci_total[m] = geonames_resp
        elif len(geonames_resp) > 1:    
            for i, resp in enumerate(geonames_resp):
                # i = -1
                # resp = geonames_resp[-1]
                if len(resp[-1]) > 1:
                    try:
                        wikipedia_link = [e for e in resp[-1] if 'wikipedia' in e][0]
                        wikipedia_title = wikipedia_link.replace('https://en.wikipedia.org/wiki/','')
                        wikipedia_query = f'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageprops&ppprop=wikibase_item&redirects=1&titles={wikipedia_title}'
                        try:
                            wikipedia_result = requests.get(wikipedia_query).json()['query']['pages']
                            wikidata_id = wikipedia_result[list(wikipedia_result.keys())[0]]['pageprops']['wikibase_item']
                            wikidata_query = requests.get(f'https://www.wikidata.org/wiki/Special:EntityData/{wikidata_id}.json').json()
                            labels = {v['value'] for k,v in wikidata_query['entities'][wikidata_id]['labels'].items()}
                            geonames_resp[i][-1].extend(labels)
                            geonames_resp[i][-1].remove(wikipedia_link)
                        # except (KeyError, requests.exceptions.ConnectTimeout):
                        except Exception:
                            pass
                    except IndexError:
                        pass
            miejscowosci_total[m] = geonames_resp
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
x = '1901'
x.isnumeric()
