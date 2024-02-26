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
from bs4 import BeautifulSoup
import endnote_credentials
import os

#%%

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