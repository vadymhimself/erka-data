import sys
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
from flask import Flask, request, jsonify, abort, render_template
from functools import wraps

# from recom.recom_interface import recommend

import logging

import resource

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
        return jsonify({'similar': []})

    if pd.isnull(drug_inst.get('atx')):
        drug_inst = get_apx_code(drug_inst)

    if pd.isnull(drug_inst.get('atx')) or drug_inst.get('atx') == '':
        product_name = drug_inst['tradeName'] if not pd.isnull(drug_inst.get('tradeName')) else drug_inst[
            'normalized_name']
        product_names = pd.concat(
            [drugs_db[drugs_db['tradeName'].isin([product_name])],
             drugs_db[drugs_db['normalized_name'].isin([product_name])]],
            ignore_index=True)
        product_names = product_names.drop_duplicates(keep='first')
        medforms = [equal_medform for medform in set(product_names['medForm'].tolist()) for equal_medform in
                    medforms_cat.get(medform, [])]
        products = drugs_db[drugs_db['medForm'].isin(medforms)]
        p = drug_inst['normalized_name']
        ps = products['normalized_name'].tolist()
        best_name = process.extractBests(p, set(ps), limit=len(ps), scorer=fuzz.token_set_ratio, score_cutoff=80)
        # import time
        # s = time.time()
        best_names_corr = []
        for name in best_name:
            if drugs_db[drugs_db['normalized_name'].isin([name[0]])]['id'].tolist()[0] not in [int(drug_name),
                                                                                               drug_name]:
                dct = dict(drugs_db[drugs_db['normalized_name'] == name[0]].iloc[0])
                dct['score'] = name[1]
                best_names_corr.append(dct)
        best_name = best_names_corr
        # print(time.time() - s )
        length_restriction = len(best_name) if not length_restriction else length_restriction
        if len(best_name) > length_restriction:
            companies = [name['company_name'] for name in best_name]
            comp_number = math.ceil(length_restriction / len(set(companies)))
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
        find = {
            'similar': [{"name": name['normalized_name'], 'id': str(name['id']), 'score': str(name['score'] / 100)} for
                        name in best_name]}

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
            'similar': [
                {'name': suggestions.iloc[i]['normalized_name'], 'id': str(suggestions.iloc[i]['id']), 'score': '1.'}
                for i
                in range(length_restriction)
                if not pd.isnull(suggestions.iloc[i]['id']) and str(suggestions.iloc[i]['id']) not in [
                    int(drug_name), drug_name]]}

    return jsonify(find)


app = Flask(__name__)
# app.logger.setLevel(logging.INFO)


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'), 403


def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        with open('apikeys.json', 'r') as apikey:
            keys = json.load(apikey)
        api_key = request.headers.get('api-key')
        if keys.get(api_key):
            keys[api_key]['requests_done'] += 1
            if keys[api_key]['quota'] >= keys[api_key]['requests_done']:
                with open('apikeys.json', 'w') as apikey:
                    json.dump(keys, apikey)
                return view_function(*args, **kwargs)
            else:
                abort(403)
        else:
            abort(401)

    return decorated_function


@app.route('/ping', methods=['GET'])
@require_apikey
def ping():
    return "pong"


@app.route('/get_similar_products', methods=['POST'])
@require_apikey
def get_similar_drugs():
    '''
    :return: json dict of lists
    '''
    drug_name = request.json['id']
    length_restriction = request.json.get('length_restriction')
    # app.logger.info('/get_similar_products endpoint receive id: ' + str(drug_name))
    res = find_similar(drug_name, length_restriction)
    # app.logger.info('/get_similar_products endpoint finish process')
    return res


# @app.route('/get_att_products', methods=['POST'])
# @require_apikey
# def get_att_drugs():
#     '''
#     :return: json dict of list
#     '''
#     drug_name = request.json['id']
#     length_restriction = request.json['length_restriction']
#     N = int(length_restriction)
#     if not isinstance(drug_name, list):
#         drug_name = [drug_name]
#
#     res = recommend(drug_name, N)
#     if res == []:
#         # can't find sutable id
#         new_drugs = []
#         for drug in drug_name:
#             [new_drugs.append(int(item['id'])) for item in json.loads(find_similar(drug, 1).data)['similar'][:3]]
#
#         res = recommend(new_drugs, N, last_trial=True)
#
#     attendants = [{"id": i['productId'], "score": i["score"]} for i in res]
#
#     find = {"attendants": attendants}
#
#     return jsonify(find)


@app.route('/get_att_products', methods=['POST'])
@require_apikey
def get_associated_products():
    '''
    :return: json dict of list
    '''
    drug_names = [str(x) for x in list(request.json['id'])]
    threshold = float(request.json['threshold'])
    # app.logger.info('/get_att_products endpoint receive id: ' + str(drug_names))

    def get_recommends(ids):
        rules = associated_rules[associated_rules.antecedents.apply(lambda x: all(item in x for item in ids))]
        rules = list(
            sorted(rules.loc[:, ['consequents', 'confidence', 'index']].values.tolist(), key=lambda x: x[1], reverse=True))

        updated_rules = []
        for s in rules:
            if s[1] >= threshold:
                rule = [int(item) for item in s[0][s[0].find("{") + 1:s[0].find("}")].split(',')]
                updated_rules.append({'products': rule, 'confidence': s[1], 'rule_id': s[2]})

        return updated_rules

    rec_prods = get_recommends(drug_names)
    find = {'associated': rec_prods}
    # app.logger.info('/get_att_products endpoint finish process')
    return jsonify(find)


if __name__ == '__main__':
    app.run(host="0.0.0.0", use_reloader=False)
