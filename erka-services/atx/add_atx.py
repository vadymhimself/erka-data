import json
import re
import urllib
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from fuzzywuzzy import process, fuzz
import pandas as pd

meds_df = pd.read_csv('meds.csv', index_col=0)
with open('meds_atx.json', 'r', encoding='utf-8') as f:
    atx_codes = json.load(f)

a = ['порошок', 'таблетки', 'мазь', 'средсвто', 'каплусы', 'раствор', 'сироп', 'спрей', 'капли', 'жидкость', 'крем',
     'гель', 'суспензия', 'смесь', 'лиофизилат', 'бальзам', 'суппозитории ректальные', 'порошок', 'эмульсия',
     'суспензия']


def get_apx_code(name):
    try:
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

        return str(td.text).strip()
    except:
        return float('NaN')


def add_atx():
    atx = []
    for index, row in meds_df.iterrows():
        if any(aa in str(row['medForm']) for aa in a):
            if row['tradeName'] == row['tradeName']:
                name = row['tradeName']
            else:
                name = row['name']
            if len(name.split()) > 1 and len(name.split()) < 6:
                atx_name = process.extractBests(name, list(atx_codes.keys()), limit=1, score_cutoff=90, )
            else:
                atx_name = process.extractBests(name, list(atx_codes.keys()), limit=1, score_cutoff=90,
                                                scorer=fuzz.ratio)

            if not atx_name and len(name.split()) < 5 and len(name) > 4:
                atx_name = get_apx_code(name)
                print(index, name, '\t', atx_name, '\tбаза')
            elif atx_name:
                atx_name = atx_codes[atx_name[0][0]]
                print(index, name, '\t', atx_name, '\tтаблетки.юа')
            else:
                atx_name = float('NaN')
                print(index, name, '\t', atx_name)

            atx.append(atx_name)
        else:
            atx_name = float('NaN')
            atx.append(atx_name)

    meds_df['atx'] = atx
    meds_df.to_csv('meds_atx.csv', index=False)


print(meds_df.head(10))
