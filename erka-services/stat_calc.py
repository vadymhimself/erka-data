import urllib
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import re
import json
import math
import pandas as pd
import pickle
from fuzzywuzzy import process, fuzz

# drugs database
PATH_DRUGS_DATABASE = 'data/meds.csv'
PATH_ASSOCIATED_RULES = 'data/rules1.csv'
PATH_MEDFORMS_CAT = 'data/medforms_small.json'
PATH_POPULAR_PRODUCTS = 'recom/data/most_popular.txt'
drugs_db = pd.read_csv(PATH_DRUGS_DATABASE)
associated_rules = pd.read_csv(PATH_ASSOCIATED_RULES)
with open(PATH_MEDFORMS_CAT, 'r') as f:
    medforms_cat = json.load(f)

def get_apx_code(product):
    try:
        if 'tradeName' in product.keys():
            name = product['tradeName']
        else:
            product['atx'] = float('NaN')

            return product

        URL = "https://grls.rosminzdrav.ru/GRLS.aspx?RegNumber=&MnnR=&lf=&TradeNmR={}&OwnerName=&MnfOrg=&MnfOrgCountry=&isfs=0&isND=-1&regtype=&pageSize=10&order=RegDate&orderType=desc&pageNum=1".format(
            urllib.parse.quote_plus(name))

        req = Request(URL, headers={
            'User-Agent': "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, "lxml")
        tr = soup.find("tr", attrs={"class": "hi_sys poi"})
        link = tr['onclick']
        first_link = 'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=' + \
                     re.findall(r"(?<=')[^']+(?=')", link)[0] + '&t='

        req = Request(first_link, headers={
            'User-Agent': "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"})
        webpage = urlopen(req).read()

        soup = BeautifulSoup(webpage, "lxml")
        div = soup.find("div", attrs={"id": "__gvctl00_plate_grATC__div"})
        tr = div.find("tr", attrs={"class": 'hi_sys'})
        td = tr.find("td")

        product['atx'] = str(td.text).strip()

        return product

    except:
        product['atx'] = float('NaN')

        return product


def find_similar(drug_name, length_restriction):
    length_restriction = length_restriction if not length_restriction else int(length_restriction)
    try:
        drug_inst = drugs_db.loc[drugs_db['id'] == int(drug_name)].iloc[0]
    except IndexError:
        return {'similar': []}

    if pd.isnull(drug_inst.get('atx')):
        drug_inst = get_apx_code(drug_inst)

    if pd.isnull(drug_inst.get('atx')) or drug_inst.get('atx') == '':
        product_name = drug_inst['tradeName'] if not pd.isnull(drug_inst.get('tradeName')) else drug_inst['normalized_name']
        product_names = pd.concat(
            [drugs_db[drugs_db['tradeName'].isin([product_name])],
             drugs_db[drugs_db['normalized_name'].isin([product_name])]],
            ignore_index=True)
        product_names = product_names.drop_duplicates(keep='first')

        medforms = [equal_medform for medform in set(product_names['medForm'].tolist()) for equal_medform in medforms_cat.get(medform, [])]
        products = drugs_db[drugs_db['medForm'].isin(medforms)]

        p = drug_inst['normalized_name']
        ps = products['normalized_name'].tolist()
        best_name = process.extractBests(p, set(ps), limit=len(ps), scorer=fuzz.token_set_ratio, score_cutoff=75)

        best_names_corr = []
        for name in best_name:
            if drugs_db[drugs_db['normalized_name'].isin([name[0]])]['id'].tolist()[0] not in [int(drug_name), drug_name]:
                dct = dict(drugs_db[drugs_db['normalized_name'] == name[0]].iloc[0])
                dct['score'] = name[1]
                best_names_corr.append(dct)
        best_name = best_names_corr

        length_restriction = len(best_name) if not length_restriction else length_restriction

        if len(best_name) > length_restriction:
            companies = [name['company_name'] for name in best_name]
            comp_number = math.ceil(length_restriction/len(set(companies)))
            if comp_number <= 1:
                best_name = best_name[:length_restriction]
            else:
                best_comp = []
                companies_set = set(companies)
                for item in companies_set:
                    num = 0
                    for name in best_name:
                        if num < comp_number and item == name['company_name']:
                            best_comp.append(name)
                            num += 1

                if len(best_comp) < length_restriction:
                    indices = [item['id'] for item in best_comp]
                    for name in best_name:
                        if len(indices) == length_restriction:
                            break
                        if name['id'] not in indices:
                            best_comp.append(name)
                            indices.append(name['id'])
                    best_name = best_comp
                else:
                    best_name = best_comp[:length_restriction]

        find = {'similar': [{"name": name['normalized_name'], 'id': str(name['id']), 'score': str(name['score'] / 100)} for name in best_name]}

    else:
        suggestions = drugs_db.loc[list(
            map(lambda x: x[:-1] == drug_inst.get('atx')[:-1] if not pd.isnull(x) and x != '' else False,
                drugs_db['atx']))]
        
        length_restriction = len(suggestions) if not length_restriction else length_restriction

        if len(suggestions) <= length_restriction:
            length_restriction = len(suggestions)
        else:
            length_restriction = length_restriction + 1

        find = {
            'similar': [{'name': suggestions.iloc[i]['normalized_name'], 'id': str(suggestions.iloc[i]['id']), 'score': '1.'} for i
                        in range(length_restriction )
                        if not pd.isnull(suggestions.iloc[i]['id']) and str(suggestions.iloc[i]['id']) not in [
                            int(drug_name), drug_name]]}
    return find

def get_similar_drugs(drug_name, length_restriction):
    
    return find_similar(drug_name, length_restriction)

lst = pd.read_csv('/home/daniil/Desktop/my_files/Projects/e-com/erka-services/data/meds.csv')['id'].values
# df = df.apply(lambda x: len(get_similar_drugs(x, None)['similar']))

from tqdm import tqdm

a = {'a': []}
for i in tqdm(range(len(lst))):
	try:
		a['a'].append(len(get_similar_drugs(lst[i], None)['similar']))
	except:
		continue
	
	if i % 150 == 0:
		df = pd.DataFrame.from_dict(a)
		df.to_csv('statistics_similar.csv')