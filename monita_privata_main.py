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
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, NoAlertPresentException, SessionNotCreatedException, ElementClickInterceptedException, InvalidArgumentException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
import endnote_credentials
import os
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, FOAF, XSD, OWL

#%%

#usunąć plik
file_path = r"C:\Users\Cezary\Documents\Monita-privata\data\exportlist.txt"
os.remove(file_path)

#download references from endnote

options = Options()

options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference("browser.download.dir", r'C:\Users\Cezary\Documents\Monita-privata\data')
options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")

browser = webdriver.Firefox(options=options)

browser.get("https://access.clarivate.com/login?app=endnote")
time.sleep(1)
login = browser.find_element('xpath', "//button[@name='login-btn']")

username_input = browser.find_element('name', 'email')
password_input = browser.find_element('name', 'password')

username = endnote_credentials.username
password = endnote_credentials.password
time.sleep(1)
username_input.send_keys(username)
time.sleep(1)
password_input.send_keys(password)
time.sleep(1)
try:
    login.click()
except NoSuchElementException:
    time.sleep(1)
    username_input.send_keys(username)
    time.sleep(1)
    password_input.send_keys(password)
    time.sleep(1)
    login.click()
time.sleep(2)
url = 'https://www.myendnoteweb.com/EndNoteWeb.html?func=export%20citations&'
browser.get(url)
time.sleep(2)
reject_cookies = browser.find_element('xpath', "//button[@id='onetrust-reject-all-handler']")
reject_cookies.click()
time.sleep(1)
references = browser.find_element('xpath', "//option[@value='YmJdcwrsDrYAAD6geaA:101']")
references.click()
time.sleep(1)
export_style = browser.find_element('xpath', "//option[@value='RefMan (RIS) Export.ens']")
export_style.click()
time.sleep(1)
save_button = browser.find_element('xpath', "//input[@name='export citations 2.x']")
save_button.click()
browser.close()


file = r"data\exportlist.txt"

# with open(file, encoding='utf-8') as bibtex_file:
#     bib_database = bibtexparser.load(bibtex_file)

# data = bib_database.entries

with open(file, encoding='utf-8') as f:
    data = f.readlines()
    
# test = set([e[:2] for e in data if '  - ' in e])
# [e for e in test if e not in conversion_dict_RIS.keys()]

data_list = []
for i, row in enumerate(data[:-1]):
    if row[2:6] == '  - ' and data[i+1][2:6] == '  - ':
        temp = row.strip()
        data_list.append(temp)
    elif row[2:6] == '  - ' and data[i+1][2:6] != '  - ':
        temp = row.strip()
    elif row[2:6] != '  - ' and data[i+1][2:6] == '  - ':
        temp += f" {row.strip()}"
        data_list.append(temp)
    elif row[2:6] != '  - ' and data[i+1][2:6] != '  - ':
        temp += f" {row.strip()}"

# data_list = []
# for i, row in enumerate(data[:-1]):
#     if row.startswith('%') and data[i+1].startswith('%'):
#         temp = row.strip()
#         data_list.append(temp)
#     elif row.startswith('%') and not data[i+1].startswith('%'):
#         temp = row.strip()
#     elif not row.startswith('%') and data[i+1].startswith('%'): 
#         temp += f" {row.strip()}"
#         data_list.append(temp)
#     elif not row.startswith('%') and not data[i+1].startswith('%'): 
#         temp += f" {row.strip()}"

bib_list = []
for row in data_list:
    # if row.startswith('%0'):
    if row.startswith('TY  - '):
        bib_list.append([row])
    else:
        if row.strip():
            bib_list[-1].append(row)
            
final_list = []
for lista in bib_list:
    slownik = {}
    for el in lista:
        if el[:2] in slownik:
            slownik[el[:2]] += f"❦{el[6:]}"
        else:
            slownik[el[:2]] = el[6:]
    final_list.append(slownik)

df = pd.DataFrame(final_list)

conversion_dict_RIS = {
    'ST': 'short_title',
    'SE': 'pages2',
    'AD': 'postal_address',
    'TY': 'type',
    'NV': 'number_of_volumes',
    'ET': 'edition',
    'M3': 'format',
    'RN': 'research_notes',
    'A4': 'NT',
    'SN': 'catalogue_info',
    'AU': 'author',
    'T2': 'secondary_title',
    'CY': 'publication_place',
    'PY': 'year',
    'A2': 'co-author',
    'LB': 'label',
    'LA': 'language',
    'PB': 'publisher',
    'KW': 'keywords',
    'CN': 'keywords2',
    'AN': 'accession_number',
    'M1': 'number',
    'SP': 'pages',
    'TI': 'title',
    'UR': 'url',
    'VL': 'volume',
    'DP': 'database_provider',
    'AB': 'abstract',
    'N1': 'notes',
    'DB': 'name_of_database',
    'ER': 'end_of_reference', 
    'ID': 'ID', 
    'RP': 'reprint_status'
    }

# conversion_dict = {
#     '%!': 'title2',
#     '%&': 'pages2',
#     '%+': 'ID',
#     '%0': 'type',
#     '%6': 'notes2',
#     '%7': 'edition',
#     '%9': 'format',
#     '%<': 'translation info',
#     '%?': 'NT',
#     '%@': 'catalogue info',
#     '%A': 'author',
#     '%B': 'note3',
#     '%C': 'address',
#     '%D': 'year',
#     '%E': 'co-author',
#     '%F': 'unknown number',
#     '%G': 'language',
#     '%I': 'publisher',
#     '%K': 'keywords',
#     '%L': 'keywords2',
#     '%M': 'library id',
#     '%N': 'number',
#     '%P': 'pages',
#     '%T': 'title',
#     '%U': 'url',
#     '%V': 'volume',
#     '%W': 'worldcat',
#     '%X': 'abstract',
#     '%Z': 'note',
#     '%~': 'worldcat2'
#     }

df.columns = [conversion_dict_RIS.get(e) for e in df.columns]

#%% records and places
records_and_places = gsheet_to_df('1Gh7ZZ9hrcygOCAFr-jVHBTKPvIIQGd-UJ4uwaA4B4o0', 'Sheet1')

# endnote_ids = df['ID'].to_list()
# rap_ids = records_and_places['ID'].to_list()
# new_ids = [e for e in endnote_ids if e not in rap_ids]

# [e for e in endnote_ids if e in ['2725', '2726', '2718', '2122', '2724']]
# new = df.loc[~df['ID'].isin(records_and_places['ID'].to_list())]

df_total = pd.merge(df, records_and_places[['ID', 'typ miejscowości', 'miejscowość w tekście', 'prawdopodobna miejscowość wydania', 'prawdziwa miejscowość wydania', 'czy wydane samodzielnie (tak / nie)', 'manuskrypt', 'do usunięcia']], how='left', on='ID')

df_select = df_total[['ID', 'year', 'title', 'typ miejscowości', 'miejscowość w tekście', 'prawdopodobna miejscowość wydania', 'prawdziwa miejscowość wydania', 'czy wydane samodzielnie (tak / nie)', 'manuskrypt', 'do usunięcia']]

df_select = df_select.loc[(df_select['manuskrypt'].isna()) &
                          (df_select['do usunięcia'].isna())].drop(columns=['manuskrypt', 'do usunięcia'])
#%% geonames_query
geonames_list = set(df_select['miejscowość w tekście'].to_list() + df_select['prawdopodobna miejscowość wydania'].to_list() + df_select['prawdziwa miejscowość wydania'].to_list())
geonames_list = set([e for e in geonames_list if isinstance(e, str)])

def query_geonames(geoname_url):
# places_with_geonames = {}
# for geoname_url in tqdm(geonames_list):
    # m = 'Dublin'
    geoname_id = re.findall('\d+', geoname_url)[0]
    url = 'http://api.geonames.org/get?'
    params = {'username': random.choice(geonames_users), 'geonameId': geoname_id, 'style': 'FULL'}
    result = requests.get(url, params=params)
    if 'status' in result:
        time.sleep(5)
        query_geonames(geoname_id)
    else:  
        soup = BeautifulSoup(result.text, "html.parser")
        temp_dict = {'name': soup.find('name').text,
                     'lat': soup.find('lat').text,
                     'lng': soup.find('lng').text,
                     'geoname_id': geoname_id}
        places_with_geonames[geoname_url] = temp_dict
    
places_with_geonames = {}
with ThreadPoolExecutor() as excecutor:
    list(tqdm(excecutor.map(query_geonames, geonames_list),total=len(geonames_list)))

#%%
year = set(df_select['year'].to_list())

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
    
df_fixed = df_select.copy()
df_fixed['year_fixed'] = df_fixed['year'].apply(lambda x: get_year(x)[0])
df_fixed['year_certainty'] = df_fixed['year'].apply(lambda x: get_year(x)[1])
    
#test poprawności funkcji `set_year`
for e in year:
    if get_year(e) == 'solution not provided':
        print(e)

def get_origin_of_the_year(x):
    if '[' in x:
        return 'external'
    else: return 'internal'
    
df_fixed['year_origin'] = df_fixed['year'].apply(lambda x: get_origin_of_the_year(x))
    
def get_privata_in_title(x):
    if 'privata' in x.lower():
        return True
    else: return False

df_fixed['privata_in_title'] = df_fixed['title'].apply(lambda x: get_privata_in_title(x))

def get_secreta_in_title(x):
    if 'secreta' in x.lower():
        return True
    else: return False   
    
df_fixed['secreta_in_title'] = df_fixed['title'].apply(lambda x: get_secreta_in_title(x))
#dopytać RM, jaka informacja i w którym polu
#def set_publishing_form(x):

#%% ontologia

#namespaces
monita = Namespace("http://purl.org/monita/")
n = Namespace("http://example.org/people/")
dcterms = Namespace("http://purl.org/dc/terms/")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
book_uri = "http://miastowies.org/item/"
eltec_uri = "http://distantreading.github.io/ELTeC/pol/"
polona_uri = "http://polona.pl/item/"
wl_uri = "https://wolnelektury.pl/katalog/lektura/"
ws_uri = "https://pl.wikisource.org/wiki/"
FABIO = Namespace("http://purl.org/spar/fabio/")
BIRO = Namespace("http://purl.org/spar/biro/")
VIAF = Namespace("http://viaf.org/viaf/")
WIKIDATA = Namespace("http://www.wikidata.org/entity/")
GEONAMES = Namespace("https://www.geonames.org/")
geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
bibo = Namespace("http://purl.org/ontology/bibo/")
schema = Namespace("http://schema.org/")
#def

g = Graph()

g.bind("monita", monita)
g.bind("dcterms", dcterms)
g.bind("fabio", FABIO)
g.bind("geo", geo)
g.bind("bibo", bibo)
g.bind("schema", schema)
g.bind("biro", BIRO)
g.bind("foaf", FOAF)

def add_place(place_dict):
    place = URIRef(k)
    g.add((place, RDF.type, dcterms.Location))
    g.add((place, RDFS.label, Literal(place_dict[k]['name'])))
    latitude = Literal(place_dict[k]["lat"], datatype=XSD.float)
    g.add((place, geo.lat, latitude))
    longitude = Literal(place_dict[k]["lng"], datatype=XSD.float)
    g.add((place, geo.long, longitude))

for k,v in places_with_geonames.items():
    add_place({k:v})

def add_book(row):
    book = URIRef(monita + row['ID'])
    g.add((book, RDF.type, dcterms.BibliographicResource))
    g.add((book, dcterms.date, Literal(row["year_fixed"], datatype = XSD.year)))
    g.add((book, monita.yearCertainty, Literal(row['year_certainty'])))
    g.add((book, monita.yearOrigin, Literal(row['year_origin'])))
    g.add((book, dcterms.title, Literal(row["title"])))
    g.add((book, monita.privataInTitle, Literal(row["privata_in_title"])))
    g.add((book, monita.secretaInTitle, Literal(row["secreta_in_title"])))
    if pd.notnull(row['czy wydane samodzielnie (tak / nie)']):
        if row['czy wydane samodzielnie (tak / nie)'] == 'tak':
            g.add((book, monita.publishedSeparately, Literal(True)))
        else: g.add((book, monita.publishedSeparately, Literal(False)))
    g.add((book, monita.placeType, Literal(row['typ miejscowości'])))
    if isinstance(row['miejscowość w tekście'], str):
        g.add((book, monita.placeInText, URIRef(row['miejscowość w tekście'])))
    if isinstance(row['prawdopodobna miejscowość wydania'], str):
        g.add((book, monita.probablePlace, URIRef(row['prawdopodobna miejscowość wydania'])))
    if isinstance(row['prawdziwa miejscowość wydania'], str):
        g.add((book, FABIO.hasPlaceOfPublication, URIRef(row['prawdziwa miejscowość wydania'])))
    
for i, row in df_fixed.iterrows():
    add_book(row)
    
g.serialize("data/monita.ttl", format = "turtle")

#https://www.youtube.com/watch?v=kyucE2iINwQ
#skopiować logi, dodać .jar do pluginów, https://neo4j.com/labs/neosemantics/4.0/install/, może być błąd, wtedy sprawdzić plugins, czy nie ma starego

#przykład
# match (book:dcterms__BibliographicResource) - [a:fabio__hasPlaceOfPublication] - (place:dcterms__Location) return book, place

#%% wizualizacja na mapie
import requests
import pandas as pd
from pathlib import Path
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objs as go

df_geonames = pd.DataFrame().from_dict(places_with_geonames, orient='index').reset_index().rename(columns={'index': 'geonames'})
df_monita = df_fixed[['ID', 'title', 'prawdziwa miejscowość wydania', 'year_fixed']].rename(columns={'prawdziwa miejscowość wydania': 'geonames'})
df_monita = df_monita.loc[df_monita['geonames'].notnull()]

df_map = pd.merge(df_monita, df_geonames, how='left', on='geonames').sort_values('year_fixed')
df_map['lat'] = df_map['lat'].astype(float)
df_map['lng'] = df_map['lng'].astype(float)
df_map['size'] = df_map.groupby(['geonames']).cumcount()+1
df_map['size'] = df_map['size'] * 2
# df_map['date'] = pd.to_datetime(df_map['year_fixed'], format='%Y')

# fig = px.scatter_mapbox(
#         df_map,
#         lat="lat",
#         lon="lng",
#         size="size",
#         hover_data=["title"],
#         animation_frame="year_fixed",
#     ).update_layout(
#         mapbox={"style": "carto-positron", "zoom":11}, margin={"l": 0, "r": 0, "t": 0, "b": 0}
#     )
    
# plot(fig, auto_open=True) 
    

fig = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lng",
        size="size",
        hover_name="name",
        hover_data=["title"],
        color_discrete_sequence=["red"],
        animation_frame="year_fixed",
        animation_group='name',
        zoom=3.75,
        center={'lat': 50.076301241046366,
                'lon': 14.427848170989792}
        )
        
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

cumulative_frames = [{"data": [{"type": "scattermapbox",
                                "lat": df_map.loc[df_map["year_fixed"] <= year, "lat"],
                                "lon": df_map.loc[df_map["year_fixed"] <= year, "lng"],
                                "mode": "markers",
                                "marker": {"size": df_map.loc[df_map["year_fixed"] <= year, "size"].tolist()},
                                "text": df_map.loc[df_map["year_fixed"] <= year, "name"].tolist(),
                                "hoverinfo": "text+name+lat+lon"}],
                      "name": str(year)}
                     for year in sorted(df_map["year_fixed"].unique())]

fig.frames = cumulative_frames

plot(fig, auto_open=True)
fig.write_html("data/monita.html")
# fig.show()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

