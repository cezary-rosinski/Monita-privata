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
from my_functions import gsheet_to_df
import json

#%%

file = r"data\endnote_bibliography.txt"

# with open(file, encoding='utf-8') as bibtex_file:
#     bib_database = bibtexparser.load(bibtex_file)

# data = bib_database.entries

with open(file, encoding='utf-8') as f:
    data = f.readlines()

data_list = []
for i, row in enumerate(data[:-1]):
    if row.startswith('%') and data[i+1].startswith('%'):
        temp = row.strip()
        data_list.append(temp)
    elif row.startswith('%') and not data[i+1].startswith('%'):
        temp = row.strip()
    elif not row.startswith('%') and data[i+1].startswith('%'): 
        temp += f" {row.strip()}"
        data_list.append(temp)
    elif not row.startswith('%') and not data[i+1].startswith('%'): 
        temp += f" {row.strip()}"

bib_list = []
for row in data_list:
    if row.startswith('%0'):
        bib_list.append([row])
    else:
        if row.strip():
            bib_list[-1].append(row)
            
final_list = []
for lista in bib_list:
    slownik = {}
    for el in lista:
        if el[:2] in slownik:
            slownik[el[:2]] += f"❦{el[3:]}"
        else:
            slownik[el[:2]] = el[3:]
    final_list.append(slownik)

df = pd.DataFrame(bib_list)

conversion_dict = {
    '%!': 'title2',
    '%&': 'pages2',
    '%+': 'ID',
    '%0': 'type',
    '%6': 'notes2',
    '%7': 'edition',
    '%9': 'format',
    '%<': 'translation info',
    '%?': 'NT',
    '%@': 'catalogue info',
    '%A': 'author',
    '%B': 'note3',
    '%C': 'address',
    '%D': 'year',
    '%E': 'co-author',
    '%F': 'unknown number',
    '%G': 'language',
    '%I': 'publisher',
    '%K': 'keywords',
    '%L': 'keywords2',
    '%M': 'library id',
    '%N': 'number',
    '%P': 'pages',
    '%T': 'title',
    '%U': 'url',
    '%V': 'volume',
    '%W': 'worldcat',
    '%X': 'abstract',
    '%Z': 'note',
    '%~': 'worldcat2'
    }
#pola mogą być wilokrotne!

year = set(df['year'].to_list())

def get_year(x):
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
    
df_fixed = df.copy()
df_fixed['year_fixed'] = df['year'].apply(lambda x: get_year(x)[0])
df_fixed['year_certainty'] = df['year'].apply(lambda x: get_year(x)[1])
    
#test poprawności funkcji `set_year`
for e in year:
    if get_year(e) == 'solution not provided':
        print(e)

def get_origin_of_the_year(x):
    if '[' in x:
        return 'external'
    else: return 'internal'
    
df_fixed['year_origin'] = df['year'].apply(lambda x: get_origin_of_the_year(x))
    
def get_privata_in_title(x):
    if 'privata' in x.lower():
        return True
    else: return False

df_fixed['privata_in_title'] = df['title'].apply(lambda x: get_privata_in_title(x))

def get_secreta_in_title(x):
    if 'secreta' in x.lower():
        return True
    else: return False   
    
df_fixed['secreta_in_title'] = df['title'].apply(lambda x: get_secreta_in_title(x))
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

df_places = pd.DataFrame().from_dict(places_with_geonames, orient='index').reset_index().rename(columns={'index': 'query'})
        
# for m in tqdm(places):
#     query_geonames(m)
        
df_places = gsheet_to_df('1Azq2_eYY2cooc9emPHlOj6vkwDrS04OdrPz-GZQ5tMI', 'Arkusz1')
df_places = df_places.loc[(df_places['error'].isnull()) & (df_places['lat'].notnull())].drop(columns='error')

df_to_work = pd.merge(df_fixed, df_places, left_on='address', right_on='query', how='left')[['ID', 'title', 'publisher', 'address', 'note', 'year', 'name', 'link']]

df_to_work.to_excel('data/records_and_places.xlsx', index=False)

#%% geojson

geo_data = gsheet_to_df('1Azq2_eYY2cooc9emPHlOj6vkwDrS04OdrPz-GZQ5tMI', 'Arkusz1')  
geo_data = geo_data.loc[(geo_data['lat'].notnull()) &
                        (geo_data['error'].isnull())]
        
geojson = {"type": "FeatureCollection", "features": []}

for _, row in geo_data.iterrows():
    feature = {"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(row['lng']), float(row['lat'])]}, "properties": {"city": row['name']}}
    geojson['features'].append(feature)
    
with open('data/monita_privata.geojson', 'w') as fp:
    json.dump(geojson, fp) 
        
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

