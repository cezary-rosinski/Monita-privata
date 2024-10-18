import sys
from SPARQLWrapper import SPARQLWrapper, JSON
from urllib.error import HTTPError, URLError
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import regex as re
from collections import defaultdict

#%% def

def wikidata_simple_dict_resp(results):
    results = results['results']['bindings']
    dd = defaultdict(list)
    for d in results:
        for key, value in d.items():
            dd[key].append(value)
    dd = {k:set([tuple(e.items()) for e in v]) for k,v in dd.items()}
    dd = {k:list([dict((x,y) for x,y in e) for e in v]) for k,v in dd.items()}
    return dd

def query_wikidata_for_people(order_id):
    order = order_id.split('/')[-1]
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
  {{
    SELECT DISTINCT ?item WHERE {{
      ?item p:P611 ?statement0.
      ?statement0 (ps:P611/(wdt:P279*)) wd:{order}.
    }}
  }}
}}""")
    sparql.setReturnFormat(JSON)
    while True:
        try:
            results = sparql.query().convert()
            break
        except HTTPError:
            time.sleep(2)
        except URLError:
            time.sleep(5)
    results = wikidata_simple_dict_resp(results)  
    people_per_order[order_id] = results
    return results

def query_wikidata_for_people_in_conflict(order_id):
    order = order_id.split('/')[-1]
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
    sparql.setQuery(f"""SELECT DISTINCT ?item ?itemLabel WHERE {{
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
  {{
    SELECT DISTINCT ?item WHERE {{
      ?item p:P611 ?statement0.
      ?statement0 (ps:P611/(wdt:P279*)) wd:{order}.
      ?item p:P607 ?statement1.
      ?statement1 (ps:P607/(wdt:P279*)) _:anyValueP607.
    }}
  }}
}}""")
    sparql.setReturnFormat(JSON)
    while True:
        try:
            results = sparql.query().convert()
            break
        except HTTPError:
            time.sleep(2)
        except URLError:
            time.sleep(5)
    results = wikidata_simple_dict_resp(results)  
    people_in_conflict[order_id] = results
    return results


#%% main
# lista zakonów z wikidaty
user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent=user_agent)
sparql.setQuery("""SELECT DISTINCT ?item ?itemLabel WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT DISTINCT ?item WHERE {
      ?item p:P31 ?statement0.
      ?statement0 (ps:P31/(wdt:P279*)) wd:Q391009.
    }
  }
}""")
sparql.setReturnFormat(JSON)

results = sparql.query().convert()

dict_of_orders = {e.get('item').get('value'):e.get('itemLabel').get('value') for e in results.get('results').get('bindings')}
list_of_orders = set(dict_of_orders.keys()) #227 orders

people_per_order = {}
with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(query_wikidata_for_people, list_of_orders), total=len(list_of_orders)))
    
people_per_order = {k:v for k,v in people_per_order.items() if v} #132 orders with people
orders_of_people_list = set(people_per_order.keys())

people_in_conflict = {}
with ThreadPoolExecutor() as executor:
    list(tqdm(executor.map(query_wikidata_for_people_in_conflict, orders_of_people_list), total=len(orders_of_people_list)))

people_in_conflict_per_order = {k:v for k,v in people_in_conflict.items() if v} #32 orders with people in conflicts

conflict_ratio_per_order = {k:len(v.get('item'))/len(people_per_order.get(k).get('item')) for k,v in people_in_conflict_per_order.items()}
conflict_ratio_per_order2 = {k:len(v.get('item'))/len(people_per_order.get(k).get('item')) for k,v in people_in_conflict_per_order.items() if len(v.get('item')) > 10}




































