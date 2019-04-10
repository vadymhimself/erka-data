import urllib
from urllib.request import Request, urlopen
import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from fuzzywuzzy import process, fuzz
from flask import Flask, request, jsonify
from flask_basicauth import BasicAuth

from recom.recom_interface import recommend

import logging
import resource

# drugs database
PATH_DRUGS_DATABASE = 'data/meds.csv'
drugs_db = pd.read_csv(PATH_DRUGS_DATABASE)

log = logging.basicConfig(level=logging.DEBUG, filename='interface.log')


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
    try:
        drug_inst = drugs_db.loc[drugs_db['id'] == int(drug_name)].iloc[0]
    except IndexError:
        return jsonify({'similar': []})

    if pd.isnull(drug_inst.get('atx')):
        drug_inst = get_apx_code(drug_inst)

    if pd.isnull(drug_inst.get('atx')) or drug_inst.get('atx') == '':
        product_name = drug_inst['tradeName'] if not pd.isnull(drug_inst.get('tradeName')) else drug_inst['name']
        product_names = pd.concat(
            [drugs_db[drugs_db['tradeName'].isin([product_name])],
             drugs_db[drugs_db['name'].isin([product_name])]],
            ignore_index=True)
        product_names = product_names.drop_duplicates(keep='first')
        products = drugs_db[drugs_db['medForm'].isin(product_names['medForm'].tolist())]

        p = drug_inst['name']
        ps = products['name'].tolist()
        best_name = process.extractBests(p, set(ps), limit=10, scorer=fuzz.token_set_ratio, score_cutoff=75)

        if len(best_name) > int(length_restriction):
            best_name = best_name[:length_restriction]

        find = {'similar': [
            {"name": name[0], 'id': drugs_db[drugs_db['name'].isin([name[0]])]['id'].tolist()[0],
             'score': name[1] / 100}
            for name in best_name if
            drugs_db[drugs_db['name'].isin([name[0]])]['id'].tolist()[0] not in [int(drug_name), drug_name]]}
    else:
        suggestions = drugs_db.loc[list(
            map(lambda x: x[:-1] == drug_inst.get('atx')[:-1] if not pd.isnull(x) and x != '' else False,
                drugs_db['atx']))]

        if len(suggestions) <= int(length_restriction):
            length_restriction = len(suggestions)
        else:
            length_restriction = length_restriction + 1

        find = {
            'similar': [{'name': suggestions.iloc[i]['name'], 'id': str(suggestions.iloc[i]['id']), 'score': '1.'} for i
                        in range(length_restriction )
                        if not pd.isnull(suggestions.iloc[i]['id']) and str(suggestions.iloc[i]['id']) not in [
                            int(drug_name), drug_name]]}
    logging.info('response ', find)
    return jsonify(find)


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'erka-services'
app.config['BASIC_AUTH_PASSWORD'] = 'erka-products'
basic_auth = BasicAuth(app)


@app.route('/ping', methods=['GET'])
@basic_auth.required
def ping():
    logging.info('Ping-Pong')
    return "pong"


@app.route('/get_similar_products', methods=['POST'])
@basic_auth.required
def get_similar_drugs():
    '''
    :return: json dict of lists
    '''
    logging.info('/get_similar_products endpoint')
    drug_name = request.json['id']
    length_restriction = request.json['length_restriction']
    # logging.info('product_id ', drug_name)
    
    return find_similar(drug_name, length_restriction)


@app.route('/get_att_products', methods=['POST'])
@basic_auth.required
def get_att_drugs():
    '''
    :return: json dict of list
    '''
    drug_name = request.json['id']
    length_restriction = request.json['length_restriction']
    N = int(length_restriction)
    if not isinstance(drug_name, list):
        drug_name = [drug_name]

    res = recommend(drug_name, N)
    if res == []:
        # can't find sutable id
        new_drugs = []
        for drug in drug_name:
            [new_drugs.append(int(item['id'])) for item in json.loads(find_similar(drug, 1).data)['similar'][:3]]

        res = recommend(new_drugs, N, last_trial=True)

    attendants = [{"id": i['productId'], "score": i["score"]} for i in res]

    find = {"attendants": attendants}

    return jsonify(find)


# def limit_memory():
#     soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#     resource.setrlimit(resource.RLIMIT_AS, (200*1024*1024, hard))
#     soft, hard = resource.getrlimit(resource.RLIMIT_VMEM)
#     resource.setrlimit(resource.RLIMIT_VMEM, (200*1024*1024, hard))

if __name__ == '__main__':
#     limit_memory()
    app.run(host="0.0.0.0", use_reloader=False)
